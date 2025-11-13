import argparse
import csv
import os
from datetime import datetime
from collections import defaultdict
from rich.console import Console
from rich.table import Table
import matplotlib.pyplot as plt

console = Console()

DATA_FILE = "expenses.csv"

# ========== 数据操作部分 ==========
def init_file():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["日期", "金额", "类别", "备注"])

def add_expense(amount, category, note):
    init_file()
    with open(DATA_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime("%Y-%m-%d"), amount, category, note])
    console.print(f"✅ 已添加账单：{amount} ({category}) - {note}", style="bold green")

def list_expenses():
    init_file()
    table = Table(title="账单记录")
    table.add_column("日期")
    table.add_column("金额")
    table.add_column("类别")
    table.add_column("备注")
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            table.add_row(row["日期"], row["金额"], row["类别"], row["备注"])
    console.print(table)

def summary_expenses():
    init_file()
    total = 0
    category_sum = defaultdict(float)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            amount = float(row["金额"])
            total += amount
            category_sum[row["类别"]] += amount
    console.print(f"\n💰 总支出：{total:.2f} 元", style="bold yellow")
    for c, v in category_sum.items():
        console.print(f"  - {c}: {v:.2f} 元", style="cyan")

def delete_last():
    init_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()
    if len(lines) > 1:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            f.writelines(lines[:-1])
        console.print("🗑️ 已删除最后一条记录", style="bold red")
    else:
        console.print("没有记录可以删除。", style="bold yellow")

# ========== 图表功能部分 ==========
def show_chart():
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm

    init_file()
    category_sum = defaultdict(float)
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            category_sum[row["类别"]] += float(row["金额"])

    if not category_sum:
        console.print("暂无数据，无法生成图表。", style="red")
        return

    categories = list(category_sum.keys())
    amounts = list(category_sum.values())

    # ✅ 设置中文字体（防止乱码）
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 或者 'Microsoft YaHei'
    plt.rcParams['axes.unicode_minus'] = False

    # ---- 饼图 ----
    plt.figure(figsize=(6, 6))
    plt.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=140)
    plt.title("各类别支出比例图", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("expense_pie_chart.png", bbox_inches="tight", dpi=200)
    plt.close()

    # ---- 柱状图 ----
    plt.figure(figsize=(8, 5))
    bars = plt.bar(categories, amounts, color="#4CA1AF", edgecolor="black")

    plt.title("各类别支出总额分布", fontsize=16, fontweight="bold")
    plt.xlabel("支出类别", fontsize=12)
    plt.ylabel("金额（元）", fontsize=12)
    plt.xticks(rotation=25)

    # ✅ 在柱子上标出金额
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.1f}",
                 ha="center", va="bottom", fontsize=10)

    plt.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig("expense_bar_chart.png", bbox_inches="tight", dpi=200)
    plt.close()

    console.print("📊 已生成图表：expense_pie_chart.png、expense_bar_chart.png", style="bold green")

# ========== 命令行部分 ==========
def main():
    parser = argparse.ArgumentParser(description="命令行记账工具（含图表）")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="添加一条支出")
    add_parser.add_argument("amount", type=float)
    add_parser.add_argument("category")
    add_parser.add_argument("note")

    subparsers.add_parser("list", help="查看所有支出")
    subparsers.add_parser("summary", help="查看支出汇总")
    subparsers.add_parser("delete", help="删除最后一条记录")
    subparsers.add_parser("chart", help="生成支出图表")

    args = parser.parse_args()

    if args.command == "add":
        add_expense(args.amount, args.category, args.note)
    elif args.command == "list":
        list_expenses()
    elif args.command == "summary":
        summary_expenses()
    elif args.command == "delete":
        delete_last()
    elif args.command == "chart":
        show_chart()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
