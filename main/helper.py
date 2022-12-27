from tkinter import *
from tkinter import messagebox
import tkinter.ttk as ttk
import os
import numpy as np
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
from tkinter import scrolledtext


# when testing on terminal, use these lines to get cwd
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
cwd = __location__ + "\\data\\"

# when creating the exe, use this line to get cwd
# cwd = "data\\"

VERSION = 1.3
LAST_UPDATED = "2022-12-26"

def main_page(root):

    # today
    today = pd.to_datetime('today')
    year = today.year
    month = today.month
    day = today.day

    # read in dfs
    works_df = pd.read_csv(cwd + "works.csv")
    status_log_df = pd.read_csv(cwd + "status_log.csv", parse_dates = [3, 4, 5], date_parser = pd.to_datetime)
    clients_df = pd.read_csv(cwd + "clients.csv")
    status_df = pd.read_csv(cwd + "status.csv")

    ### VIEW 1.0: main page
    main = Frame(root)

    # title + calendar
    main_title_frame = Frame(main)
    # title
    main_title = Label(main_title_frame, text = "Mayson和Angel的小本本~", font=("微软雅黑", 32))
    main_title.grid(row = 0)

    # calendar
    calendar = Label(main_title_frame, text = str(month) + "." + str(day), font=("微软雅黑", 24))
    calendar.grid(row = 1)
    main_title_frame.pack()

    # separator line
    separator = ttk.Separator(main, orient='horizontal')
    separator.pack(fill='x')

    # active works
    # get the latest log of each work
    status_log_df['rank'] = status_log_df.groupby('work_id')['timestamp'].rank(ascending = False)
    df = status_log_df[status_log_df['rank'] == 1].drop('rank', axis = 1)[['work_id', 'status_id', 'end_date']]
    # get active works: remove 工作完成 取消
    df = df[~df['status_id'].isin((4, 5))]
    # get info of works
    df = pd.merge(df, works_df[['id', 'name', 'client_id', 'memo']], left_on = ['work_id'], right_on = ['id']).drop(['id'], axis = 1)
    # get info of status
    df = pd.merge(df, status_df, left_on = ['status_id'], right_on = ['id']).drop(['status_id', 'id'], axis = 1)
    # get info of clients
    df = pd.merge(df, clients_df[['id', 'client']], left_on = ['client_id'], right_on = ['id']).drop(['client_id', 'id'], axis = 1)
    df = df[['work_id', 'name', 'client', 'status', 'end_date', 'memo']].sort_values(by = ['end_date']).reset_index(drop = True).fillna('')

    # for each active work, show on the view
    def work_details(work_id):
        main.destroy()
        details_page(root, work_id, main_page)

    # create a frame for canvas
    canvas_frame = Frame(main)
    # create a canvas
    canvas = Canvas(canvas_frame)
    canvas.grid(row = 0, column = 0, sticky="nsew")
    
    # add scrollbars to the canvas
    canvas_y_scrollbar = ttk.Scrollbar(canvas_frame, orient = VERTICAL, command = canvas.yview)
    canvas_y_scrollbar.grid(row=0, column=1, sticky="ns")
    canvas_x_scrollbar = ttk.Scrollbar(canvas_frame, orient = HORIZONTAL, command = canvas.xview)
    canvas_x_scrollbar.grid(row=1, column=0, sticky="ew")

    # configure the canvas
    canvas.configure(yscrollcommand = canvas_y_scrollbar.set)
    canvas.configure(xscrollcommand = canvas_x_scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox('all')))

    # a table showing active works
    active_works = Frame(canvas)
    
    # add table_frame onto canvas
    canvas.create_window((0, 0), window = active_works, anchor = 'nw')

    # headers
    header_name = Label(active_works, text = "作品名", font=("微软雅黑", 16))
    header_client = Label(active_works, text = "客户名", font=("微软雅黑", 16))
    header_status = Label(active_works, text = "状态", font=("微软雅黑", 16))
    header_end_date = Label(active_works, text = "截止日期", font=("微软雅黑", 16))
    header_memo = Label(active_works, text = "备注", font=("微软雅黑", 16))
    # grid the headers
    header_name.grid(row = 0, column = 0, padx = 20, pady = 10)
    header_client.grid(row = 0, column = 1, padx = 20, pady = 10)
    header_status.grid(row = 0, column = 2, padx = 20, pady = 10)
    header_end_date.grid(row = 0, column = 3, padx = 20, pady = 10)
    header_memo.grid(row = 0, column = 4, padx = 20, pady = 10)

    for i, row in df.iterrows():
        row_memo = row['memo']
        if len(row_memo) > 8:
            row_memo = row_memo[:8] + "..."
        active_work_i_btn = Button(active_works, text = row['name'], command= lambda row = row: work_details(row['work_id']), font=("微软雅黑", 16))
        active_work_i_client = Label(active_works, text = row['client'], font=("微软雅黑", 16))
        active_work_i_status = Label(active_works, text = row['status'], font=("微软雅黑", 16))
        active_work_i_end_date = Label(active_works, text = row['end_date'].strftime("%m-%d"), font=("微软雅黑", 16))
        active_work_i_memo = Label(active_works, text = row_memo, font=("微软雅黑", 16))

        active_work_i_btn.grid(row = i + 1, column = 0, padx = 20, pady = 10)
        active_work_i_client.grid(row = i + 1, column = 1, padx = 20, pady = 10)
        active_work_i_status.grid(row = i + 1, column = 2, padx = 20, pady = 10)
        active_work_i_end_date.grid(row = i + 1, column = 3, padx = 20, pady = 10)
        active_work_i_memo.grid(row = i + 1, column = 4, padx = 20, pady = 10)

    # active_works.pack()
    canvas_frame.pack()
    active_works.update()
    frame_width = active_works.winfo_width()
    frame_height = active_works.winfo_height()
    canvas.configure(width = min(frame_width, 1600), height = min(620, frame_height))

    # monthly earnings
    def get_monthly_earnings(year, month):
        works_df = pd.read_csv(cwd + "works.csv")
        status_log_df = pd.read_csv(cwd + "status_log.csv", parse_dates = [3, 4, 5], date_parser = pd.to_datetime)
        # no log yet
        if status_log_df.empty:
            return 0, 0
        # get the records in logs for the deposits
        df = status_log_df[status_log_df['status_id'] == 1]
        if df.empty: # no records
            return 0, 0
        # get the records that deposited in this month & year
        df = df[(df['start_date'].dt.year == year) & (df['start_date'].dt.month == month)]
        # join with the works df to get price & deposit amount
        df = pd.merge(df, works_df, left_on = ['work_id'], right_on = ['id'])
        # calculate the pending payment
        conditions = [
            (df['fully_paid'] == 1),
            (df['fully_paid'] == 0) & (df['deposited'] == 1),
            (df['deposited'] == 0)
            ]
        choices = [
            0,
            df['price'] - df['deposit'],
            df['price']
        ]
        df['pending_payment'] = np.select(conditions, choices) 
        # monthly earnings
        monthly_earnings = df['price'].sum()
        # monthly pending payments
        monthly_pending_payments = df['pending_payment'].sum()
        return monthly_earnings, monthly_pending_payments

    monthly_earnings, monthly_pending_payments = get_monthly_earnings(year, month)
    monthly_earnings_lb = Label(main, text = f"本月总收入：{int(monthly_earnings)} 元   其中待结：{int(monthly_pending_payments)} 元", font=("微软雅黑", 16))

    monthly_earnings_lb.pack()

    # buttons 
    buttons = Frame(main)

    # create new work
    def create_new_work():
        main.destroy()
        create_page(root)

    create_new_work_btn = Button(buttons, text = "创建工作", command = create_new_work, font=("微软雅黑", 16), height = 2, width = 10)
    create_new_work_btn.grid(row = 0, column = 0, padx = 20, pady = 10)

    # show works by month
    def works_by_month():
        main.destroy()
        works_by_month_page(root)

    works_by_month_btn = Button(buttons, text = "本月总览", command = works_by_month, font=("微软雅黑", 16), height = 2, width = 10)
    works_by_month_btn.grid(row = 0, column = 1, padx = 20, pady = 10)

    # small buttons
    small_buttons = Frame(buttons)
    # pending payment
    def pending_payment():
        main.destroy()
        pending_payments_page(root)

    pending_payment_btn = Button(small_buttons, text = "待结款项", command = pending_payment, font=("微软雅黑", 16))
    pending_payment_btn.grid(row = 0, column = 0, padx = 20, pady = 10)

    # all works
    def all_works():
        main.destroy()
        all_works_page(root)

    all_works_btn = Button(small_buttons, text = "工作总览", command = all_works, font=("微软雅黑", 16))
    all_works_btn.grid(row = 1, column = 0, padx = 20, pady = 10)

    # edit clients
    def edit_clients():
        main.destroy()
        edit_clients_page(root)

    edit_clients_btn = Button(small_buttons, text = "编辑客户", command = edit_clients, font=("微软雅黑", 16))
    edit_clients_btn.grid(row = 0, column = 1, padx = 20, pady = 10)

    # edit types
    def edit_types():
        main.destroy()
        edit_types_page(root)

    edit_types_btn = Button(small_buttons, text = "编辑类型", command = edit_types, font=("微软雅黑", 16))
    edit_types_btn.grid(row = 1, column = 1, padx = 20, pady = 10)

    small_buttons.grid(row = 0, column = 2, padx = 20, pady = 10)
    buttons.pack()

    # separator line
    separator = ttk.Separator(main, orient='horizontal')
    separator.pack(fill='x', expand = 1)

    # version num
    version_label = Label(main, text = f"版本号：{VERSION} 最后更新：{LAST_UPDATED}", font=("微软雅黑", 12))
    version_label.pack()
    main.pack()

def create_page(root):

    # today
    today = pd.to_datetime('today')
    year = today.year
    month = today.month
    day = today.day
        
    ### VIEW 1.1: create a new work
    create = Frame(root)

    # title
    create_title = Label(create, text = "创建一项新工作", font=("微软雅黑", 28), padx = 20, pady = 10)
    create_title.pack()

    # info of the new work
    create_info = Frame(create)
    # variables from input
    work_name = StringVar()
    work_deposit = StringVar()
    work_price = StringVar()
    work_deadline = StringVar()
    work_memo = StringVar()

    # name of work
    name_label = Label(create_info, text = "作品名", font=("微软雅黑", 16))
    name_label.grid(row = 0, column = 0, padx = 20, pady = 10, sticky = 'w')
    name_entry = Entry(create_info, textvariable = work_name, font=("微软雅黑", 16))
    name_entry.grid(row = 0, column = 1, padx = 20, pady = 10, sticky = 'w')

    # client
    client_label = Label(create_info, text = "客户", font=("微软雅黑", 16))
    client_label.grid(row = 1, column = 0, padx = 20, pady = 10, sticky = 'w')
    # get list of clients (ordered)
    clients_df = pd.read_csv(cwd + "clients.csv")
    clients_list = get_client_list()
    client_dropdown = ttk.Combobox(create_info, value = clients_list, font=("微软雅黑", 16), state="readonly")
    client_dropdown.grid(row = 1, column = 1, padx = 20, pady = 10, sticky = 'w')

    # type
    type_label = Label(create_info, text = "类型", font=("微软雅黑", 16))
    type_label.grid(row = 2, column = 0, padx = 20, pady = 10, sticky = 'w')
    # get list of types (ordered)
    types_df = pd.read_csv(cwd + "types.csv")
    types_list = get_type_list()
    type_dropdown = ttk.Combobox(create_info, value = types_list, font=("微软雅黑", 16), state="readonly")
    type_dropdown.grid(row = 2, column = 1, padx = 20, pady = 10, sticky = 'w')

    # deposit
    deposit_label = Label(create_info, text = "定金", font=("微软雅黑", 16))
    deposit_label.grid(row = 3, column = 0, padx = 20, pady = 10, sticky = 'w')
    deposit_entry = Entry(create_info, textvariable = work_deposit, font=("微软雅黑", 16))
    deposit_entry.grid(row = 3, column = 1, padx = 20, pady = 10, sticky = 'w')

    # price
    price_label = Label(create_info, text = "总价", font=("微软雅黑", 16))
    price_label.grid(row = 4, column = 0, padx = 20, pady = 10, sticky = 'w')
    price_entry = Entry(create_info, textvariable = work_price, font=("微软雅黑", 16))
    price_entry.grid(row = 4, column = 1, padx = 20, pady = 10, sticky = 'w')

    # status
    status_label = Label(create_info, text = "状态", font=("微软雅黑", 16))
    status_label.grid(row = 5, column = 0, padx = 20, pady = 10, sticky = 'w')
    # get list of clients (ordered)
    status_df = pd.read_csv(cwd + "status.csv")
    status_list = list(status_df['status'])
    status_dropdown = ttk.Combobox(create_info, value = status_list, font=("微软雅黑", 16), state="disabled")
    status_dropdown.set(status_list[1])
    status_dropdown.grid(row = 5, column = 1, padx = 20, pady = 10, sticky = 'w')

    # deadline
    deadline_label = Label(create_info, text = "截止日期", font=("微软雅黑", 16))
    deadline_label.grid(row = 6, column = 0, padx = 20, pady = 10, sticky = 'w')
    deadline_entry = Entry(create_info, textvariable = work_deadline, font=("微软雅黑", 16))
    deadline_entry.insert(END, (today + timedelta(days = 7)).strftime("%Y-%m-%d"))
    deadline_entry.grid(row = 6, column = 1, padx = 20, pady = 10, sticky = 'w')

    # memo
    memo_label = Label(create_info, text = "备注", font=("微软雅黑", 16))
    memo_label.grid(row = 7, column = 0, padx = 20, pady = 10, sticky = 'w')
    memo_entry = Entry(create_info, textvariable = work_memo, font=("微软雅黑", 16))
    memo_entry.grid(row = 7, column = 1, padx = 20, pady = 10, sticky = 'w')

    create_info.pack()

    # buttons
    create_buttons = Frame(create)

    def create_submit():
    
        # read in dfs
        works_df = pd.read_csv(cwd + "works.csv")
        status_log_df = pd.read_csv(cwd + "status_log.csv", parse_dates = [3, 4, 5], date_parser = pd.to_datetime)
        
        # formatting
        deposit = work_deposit.get()
        if deposit == "":
            deposit = 0
        deposit = int(deposit)
        price = work_price.get()
        if price == "":
            price = 0
        price = int(price)
        # alert if deposit > price
        if price < deposit:
            messagebox.showwarning("坏了", f"总价不可小于定金！")
            return

        # get info from input
        work_id = works_df.shape[0] + 1
        status_log_id = status_log_df.shape[0] + 1
        name = work_name.get()
        client_name = client_dropdown.get()
        client_id = clients_df[clients_df['client'] == client_name].iloc[0]['id']
        type_index = type_dropdown.current()
        type_id = types_df.loc[type_index]['id']
        status_index = status_dropdown.current()
        status_id = status_df.loc[status_index]['id']
        start_date = today.strftime("%Y-%m-%d")
        end_date = work_deadline.get()
        memo = work_memo.get()

        # create a new row in the works df
        new_work = pd.DataFrame({
            "id": [work_id],
            "name": [name],
            "client_id": [client_id],
            "type_id": [type_id],
            "deposit": [deposit],
            "price": [price],
            "deposited": [0],
            "fully_paid": [0],
            "memo": [memo],
            "client_requests": [""],
            "attachments": [""]
        })
        works_df = pd.concat([works_df, new_work])
        works_df.to_csv(cwd + "works.csv", index = False)

        # create a new row in the status_log df
        new_status_log = pd.DataFrame({
            "id": [status_log_id],
            "work_id": [work_id],
            "status_id": [status_id],
            "start_date": [start_date],
            "end_date": [end_date],
            "timestamp": [dt.now()]
        })
        status_log_df = pd.concat([status_log_df, new_status_log])
        status_log_df.to_csv(cwd + "status_log.csv", index = False)

        create.destroy()
        details_page(root, work_id, main_page)
        # main_page(root)

    def create_cancel():
        create.destroy()
        main_page(root)

    create_submit_btn = Button(create_buttons, text = "确认", command = create_submit, font=("微软雅黑", 16))
    create_cancel_btn = Button(create_buttons, text = "取消", command = create_cancel, font=("微软雅黑", 16))
    create_submit_btn.grid(row = 0, column = 0, padx = 20, pady = 10, ipadx = 20)
    create_cancel_btn.grid(row = 0, column = 1, padx = 20, pady = 10, ipadx = 20)
    create_buttons.pack()

    create.pack()

def works_by_month_page(root):
    
    ### VIEW 1.7: works by month
    page_frame = Frame(root)

    # title
    title = Label(page_frame, text = "本月总览", font=("微软雅黑", 32))
    title.pack()

    # read in dfs
    works_df = pd.read_csv(cwd + "works.csv")
    status_log_df = pd.read_csv(cwd + "status_log.csv", parse_dates = [3, 4, 5], date_parser = pd.to_datetime)
    clients_df = pd.read_csv(cwd + "clients.csv")
    status_df = pd.read_csv(cwd + "status.csv")

    # create a frame for canvas
    canvas_frame = Frame(page_frame)
    # create a canvas
    canvas = Canvas(canvas_frame)
    canvas.grid(row = 0, column = 0, sticky="nsew")
    
    # add scrollbars to the canvas
    canvas_y_scrollbar = ttk.Scrollbar(canvas_frame, orient = VERTICAL, command = canvas.yview)
    canvas_y_scrollbar.grid(row=0, column=1, sticky="ns")
    canvas_x_scrollbar = ttk.Scrollbar(canvas_frame, orient = HORIZONTAL, command = canvas.xview)
    canvas_x_scrollbar.grid(row=1, column=0, sticky="ew")

    # configure the canvas
    canvas.configure(yscrollcommand = canvas_y_scrollbar.set)
    canvas.configure(xscrollcommand = canvas_x_scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox('all')))

    # table contents
    table_frame = Frame(canvas)

    # add table_frame onto canvas
    canvas.create_window((0, 0), window = table_frame, anchor = 'nw')

    # dfs to show
    df = works_df[['id', 'name', 'client_id', 'memo', 'price']].rename(columns = {'id': 'work_id'}).fillna('')
    # get client names
    df = df.merge(clients_df[['id', 'client']], left_on = "client_id", right_on = "id", suffixes=('_work', '_client')).drop('id', axis = 1) # drop repetitive client id

    # get create_date for each work (for monthly filtering)
    status_log_df['rank'] = status_log_df.groupby('work_id')['timestamp'].rank(ascending = True) # TRUE here for create date
    earliest_logs = status_log_df[status_log_df['rank'] == 1][['work_id', 'start_date']].rename(columns={"start_date": "create_date"})
    status_log_df.drop('rank', axis = 1, inplace = True)
    # merge create date to df
    df = df.merge(earliest_logs, on = "work_id")

    # get latest log for each work
    status_log_df['rank'] = status_log_df.groupby('work_id')['timestamp'].rank(ascending = False)
    latest_logs = status_log_df[status_log_df['rank'] == 1]
    status_log_df.drop('rank', axis = 1, inplace = True)
    # get latest status name for each work that's not fully paid
    df = df.merge(latest_logs[['work_id', 'status_id']], on = "work_id")
    df = df.merge(status_df, left_on = 'status_id', right_on = 'id').drop('id', axis = 1) # drop repetitive status id

    # sort by start date
    df = df.sort_values(by = "create_date").reset_index()

    # for each active work, show on the view
    def work_details(work_id):
        page_frame.destroy()
        details_page(root, work_id, works_by_month_page)

    def construct_work_table(df, starting_row):
        # remove current widgets
        for widget in table_frame.winfo_children():
            widget.destroy()

        # headers
        header_name = Label(table_frame, text = "作品名", font=("微软雅黑", 16))
        header_client = Label(table_frame, text = "客户名", font=("微软雅黑", 16))
        header_status = Label(table_frame, text = "状态", font=("微软雅黑", 16))
        header_price = Label(table_frame, text = "总价", font=("微软雅黑", 16))
        header_memo = Label(table_frame, text = "备注", font=("微软雅黑", 16))
        # grid the headers
        header_name.grid(row = 0, column = 0, padx = 20, pady = 10)
        header_client.grid(row = 0, column = 1, padx = 20, pady = 10)
        header_status.grid(row = 0, column = 2, padx = 20, pady = 10)
        header_price.grid(row = 0, column = 3, padx = 20, pady = 10)
        header_memo.grid(row = 0, column = 4, padx = 20, pady = 10, sticky = 'w')

        # separator line
        separator = ttk.Separator(table_frame, orient='horizontal')
        separator.grid(row = 1, column = 0, columnspan = 5, sticky="ew")
        
        # keep track of monthly total
        total = 0

        # construct new widgets
        df_reset_index = df.reset_index()
        for i, row in df_reset_index.iterrows():
            # show the work details
            active_work_i_btn = Button(table_frame, text = row['name'], command= lambda row = row: work_details(row['work_id']), font=("微软雅黑", 16))
            active_work_i_client = Label(table_frame, text = row['client'], font=("微软雅黑", 16))
            active_work_i_status = Label(table_frame, text = row['status'], font=("微软雅黑", 16))
            active_work_i_price = Label(table_frame, text = row['price'], font=("微软雅黑", 16))
            active_work_i_memo = Label(table_frame, text = row['memo'], font=("微软雅黑", 16))
            # grid the details
            active_work_i_btn.grid(row = i + starting_row, column = 0, padx = 20, pady = 10)
            active_work_i_client.grid(row = i + starting_row, column = 1, padx = 20, pady = 10)
            active_work_i_status.grid(row = i + starting_row, column = 2, padx = 20, pady = 10)
            active_work_i_price.grid(row = i + starting_row, column = 3, padx = 20, pady = 10)
            active_work_i_memo.grid(row = i + starting_row, column = 4, padx = 20, pady = 10, sticky = 'w')
            # keep track of monthly total
            total += row['price']

        # separator line
        separator2 = ttk.Separator(table_frame, orient='horizontal')
        separator2.grid(row = df_reset_index.shape[0] + starting_row + 1, column = 0, columnspan = 5, sticky="ew")
        
        # total
        total_row = df_reset_index.shape[0] + starting_row + 2
        total_label = Label(table_frame, text = "总计：", font=("微软雅黑", 16))
        total_label.grid(row = total_row, column = 2)
        total_amt = Label(table_frame, text = total, font=("微软雅黑", 16))
        total_amt.grid(row = total_row, column = 3)

        # table_frame.pack() 
        canvas_frame.pack()
        table_frame.update()
        frame_width = table_frame.winfo_width()
        frame_height = table_frame.winfo_height()
        canvas.configure(width = min(frame_width, 1600), height = min(850, frame_height))

    def filter_records(_):
        year_month = year_month_dropdown.get()
        
        # when not selected, show current year/month 
        if not year_month:
            select_year = dt.now().year
            selected_month = dt.now().month
        # when selected, show selected year/month
        else:
            select_year = int(year_month.split("-")[0])
            selected_month = int(year_month.split("-")[1])

        # only show the works started in selected month
        filtered_df = df[(df['create_date'].dt.year == select_year) & (df['create_date'].dt.month == selected_month)]

        construct_work_table(filtered_df, 2)  
        return_btn.focus()

    # filter by year/month
    filter_frame = Frame(page_frame)
    filter_label = Label(filter_frame, text = "选择显示月份：", font=("微软雅黑", 16))
    filter_label.grid(row = 0, column = 0)
    
    # a list of applicable year/month
    available_year_month = status_log_df['start_date'].apply(lambda x: x.strftime('%Y-%m')).drop_duplicates().sort_values(ascending=False)
    year_month_list = list(available_year_month)

    # dropdown box
    year_month_dropdown = ttk.Combobox(filter_frame, value = year_month_list, font=("微软雅黑", 16), state="readonly")
    year_month_dropdown.bind("<<ComboboxSelected>>", filter_records)
    year_month_dropdown.grid(row = 0, column = 1)
    filter_frame.pack()
    
    # list the works of current month
    select_year = dt.now().year
    selected_month = dt.now().month
    filtered_df = df[(df['create_date'].dt.year == select_year) & (df['create_date'].dt.month == selected_month)]
    construct_work_table(filtered_df, 2)  

    # return button
    def return_to_main_page():
        page_frame.destroy()
        main_page(root)

    return_btn = Button(page_frame, text = "返回", command = return_to_main_page, font=("微软雅黑", 16))
    return_btn.pack()

    page_frame.pack()

def details_page(root, work_id, previous_page):
    
    # today
    today = pd.to_datetime('today')
    year = today.year
    month = today.month
    day = today.day

    # read dfs
    works_df = pd.read_csv(cwd + "works.csv")
    status_log_df = pd.read_csv(cwd + "status_log.csv", parse_dates = [3, 4, 5], date_parser = pd.to_datetime)
    clients_df = pd.read_csv(cwd + "clients.csv")
    types_df = pd.read_csv(cwd + "types.csv")
    status_df = pd.read_csv(cwd + "status.csv")

    ### VIEW 1.2: work details
    details = Frame(root)

    # title
    details_title_frame = Frame(details)
    details_title = Label(details_title_frame, text = "工作详情", font=("微软雅黑", 28), padx = 20, pady = 10)
    details_title.pack()
    details_title_frame.pack()

    # infos - merge all relative dfs for easy reference
    df = status_log_df[status_log_df['work_id'] == work_id].sort_values(
        by = ['timestamp'], ascending = False)[:1][['work_id', 'status_id', 'end_date']]
    df = pd.merge(df, works_df[works_df['id'] == work_id], 
        left_on = ['work_id'], right_on = ['id']).drop(['id', 'work_id'], axis = 1)
    df = pd.merge(df, clients_df, left_on = ['client_id'], 
        right_on = ['id']).drop(['id', 'client_id'], axis = 1)
    df = pd.merge(df, types_df, left_on = ['type_id'], 
        right_on = ['id']).drop(['id', 'type_id'], axis = 1)
    df = pd.merge(df, status_df, left_on = ['status_id'], 
        right_on = ['id']).drop(['id', 'status_id'], axis = 1)
    info = df.loc[0].fillna('')

    # variables from input
    work_name = StringVar()
    work_deposit = StringVar()
    work_price = StringVar()
    deposited = IntVar() 
    fully_paid = IntVar() 
    work_deadline = StringVar()
    # work_name.get() to get the value
    # memo and requests are Text wigets. use textbox.get()

    # frame for infos
    details_info = Frame(details)

    # name of work
    name_label = Label(details_info, text = "作品名", font=("微软雅黑", 16))
    name_label.grid(row = 0, column = 0, padx = 20, pady = 10, sticky = 'w')
    name_entry = Entry(details_info, textvariable = work_name, font=("微软雅黑", 16))
    name_entry.insert(END, info['name'])
    name_entry.grid(row = 0, column = 1, padx = 20, pady = 10, sticky = 'w')

    # client
    client_label = Label(details_info, text = "客户", font=("微软雅黑", 16))
    client_label.grid(row = 0, column = 2, padx = 20, pady = 10, sticky = 'w')
    # get list of clients (ordered)
    clients_list = get_client_list()
    client_dropdown = ttk.Combobox(details_info, value = clients_list, font=("微软雅黑", 16), state="readonly")
    client_dropdown.set(info['client'])
    client_dropdown.grid(row = 0, column = 3, padx = 20, pady = 10, sticky = 'w')

    # type
    type_label = Label(details_info, text = "类型", font=("微软雅黑", 16))
    type_label.grid(row = 0, column = 4, padx = 20, pady = 10, sticky = 'w')
    # get list of types (ordered)
    types_list = get_type_list()
    type_dropdown = ttk.Combobox(details_info, value = types_list, font=("微软雅黑", 16), state="readonly")
    type_dropdown.set(info['type'])
    type_dropdown.grid(row = 0, column = 5, padx = 20, pady = 10, sticky = 'w')

    # deposit
    deposit_label = Label(details_info, text = "定金", font=("微软雅黑", 16))
    deposit_label.grid(row = 1, column = 0, padx = 20, pady = 10, sticky = 'w')
    deposit_entry = Entry(details_info, textvariable = work_deposit, font=("微软雅黑", 16))
    deposit_entry.insert(END, int(info['deposit']))
    deposit_entry.grid(row = 1, column = 1, padx = 20, pady = 10, sticky = 'w')

    # price
    price_label = Label(details_info, text = "总价", font=("微软雅黑", 16))
    price_label.grid(row = 1, column = 2, padx = 20, pady = 10, sticky = 'w')
    price_entry = Entry(details_info, textvariable = work_price, font=("微软雅黑", 16))
    price_entry.insert(END, int(info['price']))
    price_entry.grid(row = 1, column = 3, padx = 20, pady = 10, sticky = 'w')

    # deposited
    deposited_btn = Checkbutton(details_info, text = "定金已收", variable = deposited, 
        onvalue = 1, offvalue = 0, font=("微软雅黑", 16))
    deposited_btn.grid(row = 1, column = 4, padx = 20, pady = 10, sticky = 'w')
    
    # fully paid
    fully_paid_btn = Checkbutton(details_info, text = "全款已结", variable = fully_paid, 
        onvalue = 1, offvalue = 0, font=("微软雅黑", 16), bd = 10)
    fully_paid_btn.grid(row = 1, column = 5, padx = 20, pady = 10, sticky = 'w')

    # check the buttons if needed
    if works_df[works_df['id'] == work_id].iloc[0]['fully_paid'] == 1:
        fully_paid_btn.select()
        deposited_btn.select()
    elif works_df[works_df['id'] == work_id].iloc[0]['deposited'] == 1:
        deposited_btn.select()

    # deadline  
    deadline_label = Label(details_info, text = "截止日期", font=("微软雅黑", 16))
    deadline_label.grid(row = 2, column = 2, padx = 20, pady = 10, sticky = 'w')
    deadline_entry = Entry(details_info, textvariable = work_deadline, font=("微软雅黑", 16))
    deadline_entry.insert(END, info['end_date'].strftime("%Y-%m-%d"))
    deadline_entry.grid(row = 2, column = 3, padx = 20, pady = 10, sticky = 'w')
    
    # disable the deadline entry when work is done or cancelled
    def status_selected(_):
        if status_dropdown.get() in ("工作完成", "取消"):
            deadline_entry.delete(0, END)
            deadline_entry.configure(state = 'disable')
        else:
            deadline_entry.configure(state = 'normal')
            if not deadline_entry.get():
                deadline_entry.insert(END, info['end_date'].strftime("%Y-%m-%d"))

    # status
    status_label = Label(details_info, text = "状态", font=("微软雅黑", 16))
    status_label.grid(row = 2, column = 0, padx = 20, pady = 10, sticky = 'w')
    # get list of clients (ordered)
    status_df = pd.read_csv(cwd + "status.csv")
    status_list = list(status_df['status'])
    status_dropdown = ttk.Combobox(details_info, value = status_list, font=("微软雅黑", 16), state="readonly")
    status_dropdown.set(info['status'])
    status_dropdown.bind("<<ComboboxSelected>>", status_selected)
    status_dropdown.grid(row = 2, column = 1, padx = 20, pady = 10, sticky = 'w')

    # history status
    def history_status():
        # pop up window
        hist_status_view = Toplevel()
        work_name = works_df[works_df['id'] == work_id].iloc[0]['name']
        hist_status_view.title(work_name)
        # info
        hist_status_title_label = Label(hist_status_view, text = "历史状态", font=("微软雅黑", 22))
        hist_status_title_label.pack()

        # show history status
        logs_frame = Frame(hist_status_view)
        history_logs = status_log_df[status_log_df['work_id'] == work_id].reset_index()
        for i, row in history_logs.iterrows():
            start_date_label = Label(logs_frame, text = history_logs['start_date'].dt.date.iloc[i], font=("微软雅黑", 16))
            start_date_label.grid(row = i, column = 0, padx = 20, pady = 10, sticky = 'w')
            status_id = history_logs.iloc[i]['status_id']
            status_name = status_df[status_df['id'] == status_id].iloc[0]['status']
            status_label = Label(logs_frame, text = status_name, font=("微软雅黑", 16))
            status_label.grid(row = i, column = 1, padx = 20, pady = 10, sticky = 'w')
        logs_frame.pack()

    history_status_btn = Button(details_info, text = "历史状态", font=("微软雅黑", 16), command = history_status)
    history_status_btn.grid(row = 2, column = 4, ipadx = 20, ipady = 2)

    # memo
    memo_label = Label(details_info, text = "备注", font=("微软雅黑", 16))
    memo_label.grid(row = 3, column = 0, padx = 20, pady = 10, sticky = 'w')
    memo_entry = Text(details_info, height = 1, font=("微软雅黑", 16))
    memo_entry.insert(END, info['memo'])
    memo_entry.grid(row = 3, column = 1, columnspan = 5, padx = 20, pady = 10, sticky = 'ew')

    # client requests
    requests_label = Label(details_info, text = "客户要求", font=("微软雅黑", 16))
    requests_label.grid(row = 4, column = 0, padx = 20, pady = 10, sticky = 'w')
    requests_entry = scrolledtext.ScrolledText(details_info, wrap = WORD, height = 10, font=("微软雅黑", 16))
    requests_entry.insert(END, info['client_requests'])
    requests_entry.grid(row = 4, column = 1, columnspan = 5, padx = 20, pady = 10, sticky = 'ew')

    # # attachments
    # def add_attachment():
    #     pass
    # add_attachment_btn = Button(details_info, text = "添加附件", font=("微软雅黑", 16), command = add_attachment)
    # add_attachment_btn.grid(row = 5, column = 0)
    # attachments = info['attachments'].split(",")
    # for i in range(len(attachments)):
    #     attachment_label_i = Label(details_info, text = attachments[i], font=("微软雅黑", 16))
    #     attachment_label_i.grid(row = 5 + i, column = 1, padx = 20, pady = 10, sticky = 'w')

    # buttons
    # save the updated info on details page
    def details_save():
        
        # formatting
        deposit = work_deposit.get()
        if deposit == "":
            deposit = 0
        deposit = int(deposit)
        price = work_price.get()
        if price == "":
            price = 0
        price = int(price)

        # alert if deposit > price
        if price < deposit:
            messagebox.showwarning("坏了", f"总价不可小于定金！")
            return

        client_name = client_dropdown.get()
        type_name = type_dropdown.get()
        client_id = clients_df[clients_df['client'] == client_name]['id'].values[0]
        type_id = types_df[types_df['type'] == type_name]['id'].values[0]

        ### update works df
        works_df.loc[works_df['id'] == work_id, [
            'name', 
            'client_id', 
            'type_id', 
            'deposit', 
            'price', 
            'deposited', 
            'fully_paid', 
            'memo', 
            'client_requests'
            ]] = work_name.get(), \
                int(client_id), \
                int(type_id), \
                deposit, \
                price, \
                int(deposited.get()), \
                int(fully_paid.get()), \
                memo_entry.get("1.0", END).rstrip(), \
                requests_entry.get("1.0", END).rstrip() # for the auto-added new line character
        works_df.to_csv(cwd + "works.csv", index = False)

        ### update status_log_df
        # since status can go back and forth depending on the situation i.e. 提交，修改，提交，修改, 
        # multiple occurrence of the same status for the same work is allowed
        # check if the status was changed
        status_new = status_dropdown.get()
        status_new_id = status_df[status_df['status'] == status_new]['id'].iloc[0]
        # the lines containing the status logs for this work, sorted descendingly
        status_old_line = status_log_df[status_log_df['work_id'] == work_id].sort_values(by=['timestamp'], ascending = False) # will select the first line later
        # the index of this line
        status_old_index = status_old_line.index[0]
        # get the latest log of this work
        status_old_line = status_old_line.reset_index().iloc[0]
        # get the status id of this log
        status_old_id = status_old_line['status_id']
        # get the deadlines
        new_deadline = work_deadline.get()
        if not new_deadline: # no new deadline - work is done or cancelled
            new_deadline = dt.now()
        else:
            new_deadline_strs = new_deadline.split("-")
            new_deadline = dt(year = int(new_deadline_strs[0]), month = int(new_deadline_strs[1]), day = int(new_deadline_strs[2]))

        # if the status is not changed
        if status_new_id == status_old_id:
            old_deadline = status_old_line['end_date'].to_pydatetime()
            # but deadline is changed
            if new_deadline != old_deadline:
                # update the deadline on the existing line in log
                status_log_df.at[status_old_index, 'end_date'] = new_deadline
                status_log_df.at[status_old_index, 'timestamp'] = dt.now()
            else:
                pass

        # if the status is changed
        else:
            # current num of rows 
            row = status_log_df.shape[0]
            # add a new line to the log
            status_log_df.loc[row] = [row, work_id, status_new_id, today, new_deadline, dt.now()]
            # update the end date of the line of the previous status
            status_log_df.at[status_old_index, 'end_date'] = today
        
        # save
        status_log_df.to_csv(cwd + "status_log.csv", index = False)

        # close the work details page and go back to main page
        details_cancel()        

    def details_cancel():
        # close the work details page and go back to main page
        details.destroy()
        previous_page(root)

    details_cancel_btn = Button(details_info, text = "取消", font=("微软雅黑", 16), command = details_cancel)
    details_cancel_btn.grid(row = 6, column = 4, ipadx = 10, ipady = 10)

    details_save_btn = Button(details_info, text = "保存并返回", font=("微软雅黑", 16), command = details_save)
    details_save_btn.grid(row = 6, column = 5, ipadx = 10, ipady = 10)

    details_info.pack()
    details.pack()

def get_client_list():
    """
    :type:
    :rtype: list of strs
    return a ordered list of active clients
    """
    clients_df = pd.read_csv(cwd + "clients.csv")
    active_clients = clients_df[clients_df['active'] == 1]
    ordered_clients = active_clients.sort_values(by=['order'])
    client_list = list(ordered_clients['client'])
    return client_list
    
def get_type_list():
    """
    :type:
    :rtype: list of strs
    return a ordered list of active types
    """
    types_df = pd.read_csv(cwd + "types.csv")
    active_types = types_df[types_df['active'] == 1]
    ordered_types = active_types.sort_values(by=['order'])
    type_list = list(ordered_types['type'])
    return type_list
    
def edit_clients_page(root):
    ### VIEW 1.3: edit clients
    edit_items_page(root, "client", "客户")

def edit_types_page(root):
    ### VIEW 1.4: edit types
    edit_items_page(root, "type", "类型")

def edit_items_page(root, item_eng, item_chn):
    
    edit_items_frame = Frame(root)

    # title    
    details_edit_items_title = Label(edit_items_frame, text = f"编辑{item_chn}", font=("微软雅黑", 28), padx = 20, pady = 10)
    details_edit_items_title.pack()

    # info label
    info = Label(edit_items_frame, text = f"  上移/下移可调整下拉菜单中显示顺序，隐藏{item_chn}不显示  ", font=("微软雅黑", 12))
    info.pack()

    # helper functions for grey prompt that disappears on focus
    def handle_focus_in(_):
        new_item_entry.delete(0, END)
        new_item_entry.config(fg = 'black')

    def handle_focus_out(_):
        new_item_entry.delete(0, END)
        new_item_entry.config(fg = 'grey')
        new_item_entry.insert(0, f"新{item_chn}名")

    # add a new item
    def add_new_item():
        name = new_item_name.get()
        # item name can't be an empty string + prevent accidental addition
        if name == "" or name == f'新{item_chn}名':
            return
        # no repetitive item name - will break the logic
        if name in list(items_df[item_eng]):
            messagebox.showwarning("坏了", f"{item_chn}名不可重复！")
            return

        # add a new line to the items_df
        i = items_df.shape[0]
        if i == 0:
            existing_largest_id = -1
            existing_largest_order = 0
        else:
            existing_largest_id = max(items_df['id'])
            existing_largest_order = max(items_df['order'])
        items_df.loc[i] = [existing_largest_id + 1, name, 1, existing_largest_order + 1] # id, item, active, order # id starts from 0, order starts from 1
        items_df.to_csv(cwd + f"{item_eng}s.csv", index = False)
        items_listbox.insert(END, name)
        new_item_btn.focus()
        
    new_item_frame = Frame(edit_items_frame)

    # grey prompt in Entry box, disappear when focus in
    new_item_name = StringVar()
    new_item_entry = Entry(new_item_frame, textvariable = new_item_name, font=("微软雅黑", 16), fg = 'grey')
    new_item_entry.insert(0, f"新{item_chn}名")
    new_item_entry.bind("<FocusIn>", handle_focus_in)
    new_item_entry.bind("<FocusOut>", handle_focus_out)
    new_item_entry.grid(row = 0, column = 0, columnspan = 2, padx = 20, pady = 10, sticky = 'w')

    new_item_btn = Button(new_item_frame, text = "添加", command = add_new_item, font=("微软雅黑", 16))
    new_item_btn.grid(row = 0, column = 2, padx = 20, pady = 10, sticky = 'w')
    
    new_item_frame.pack()

    # listbox of items
    item_list_frame = Frame(edit_items_frame)

    listbox_frame = Frame(item_list_frame)
    items_df = pd.read_csv(cwd + f"{item_eng}s.csv").sort_values(by = "order")
    items_listbox = Listbox(listbox_frame, font = ("微软雅黑", 16))
    items_list = list(items_df[item_eng])

    for i in range(len(items_list)):
        item_name = items_list[i]
        items_listbox.insert(END, item_name)
        active_status = items_df[items_df[item_eng] == item_name].iloc[0]['active']
        # check for greyed out types
        if active_status == 0:
            items_listbox.itemconfig(i, fg="grey")

    items_listbox.pack(side = LEFT, fill = BOTH)
    listbox_frame.grid(row = 0, column = 0, columnspan = 2)
    # add a scroll bar to listbox

    listbox_scrollbar = Scrollbar(listbox_frame)
    listbox_scrollbar.pack(side = RIGHT, fill = BOTH)  
    items_listbox.config(yscrollcommand = listbox_scrollbar.set)
    listbox_scrollbar.config(command = items_listbox.yview)
    
    def move_up():
        # get the selected line and the line above
        selection = items_listbox.curselection()
        if not selection: # no selection
            return
        selected_index = selection[0]
        if selected_index == 0: # already at top of listbox
            return
        above_index = selected_index - 1
        selected_value = items_listbox.get(selected_index)
        above_value = items_listbox.get(above_index)
        
        # check for greyed out value
        selective_active = items_df[items_df[item_eng] == selected_value].iloc[0]['active']
        above_active = items_df[items_df[item_eng] == above_value].iloc[0]['active']

        # move
        items_listbox.delete(above_index, above_index)
        items_listbox.insert(above_index, selected_value)
        items_listbox.delete(selected_index, selected_index)
        items_listbox.insert(selected_index, above_value)

        # reassign greyed out color
        if not selective_active:
            items_listbox.itemconfig(above_index, fg="grey")
        if not above_active:
            items_listbox.itemconfig(selected_index, fg="grey")

        # auto-select the previous selection value
        items_listbox.select_set(above_index)

    def move_down():
        # get the selected line and the line below
        selection = items_listbox.curselection()
        if not selection: # no selection
            return
        selected_index = selection[0]
        if selected_index == items_listbox.size() - 1: # already at bottom of listbox
            return
        selected_value = items_listbox.get(selected_index)
        below_index = selected_index + 1
        below_value = items_listbox.get(below_index)

        # check for greyed out value
        selective_active = items_df[items_df[item_eng] == selected_value].iloc[0]['active']
        below_active = items_df[items_df[item_eng] == below_value].iloc[0]['active']
        
        # move
        items_listbox.delete(below_index, below_index)
        items_listbox.insert(below_index, selected_value)
        items_listbox.delete(selected_index, selected_index)
        items_listbox.insert(selected_index, below_value)

        # reassign greyed out color
        if not selective_active:
            items_listbox.itemconfig(below_index, fg="grey")
        if not below_active:
            items_listbox.itemconfig(selected_index, fg="grey")

        # auto-select the previous selection value
        items_listbox.select_set(below_index)

    # move up and down button
    listbox_btn_frame = Frame(item_list_frame)
    up_btn = Button(listbox_btn_frame, text = "上移", command = move_up, font=("微软雅黑", 16))
    up_btn.grid(row = 0, column = 0, padx = 20, pady = 10, sticky = 'w')
    down_btn = Button(listbox_btn_frame, text = "下移", command = move_down, font=("微软雅黑", 16))
    down_btn.grid(row = 1, column = 0, padx = 20, pady = 10, sticky = 'w')
    listbox_btn_frame.grid(column = 2, row = 0)
    item_list_frame.pack()
    
    # buttons
    new_items_btns_frame = Frame(edit_items_frame)
    
    def item_delete():
        item_name = items_listbox.get(ANCHOR)
        item_id = items_df[items_df[item_eng] == item_name].iloc[0]['id']
        works_df = pd.read_csv(cwd + "works.csv")
        # this item is not associated with any work
        if works_df[works_df[f'{item_eng}_id'] == item_id].empty:
            # ok to delete
            # delete from listbox
            selection_index = items_listbox.curselection()
            items_listbox.delete(selection_index, selection_index)
            # delete from items_df
            items_df.drop(items_df[items_df[item_eng] == item_name].index, inplace = True)
            items_df.to_csv(cwd + f'{item_eng}s.csv', index = False)
        else:
            # not ok to delete
            messagebox.showwarning("坏了", f"此{item_chn}曾出现在历史记录中，不可删除！")

    def item_on_off():
        item_name = items_listbox.get(ANCHOR)
        items_df_line = items_df[items_df[item_eng] == item_name]
        if items_df_line.shape[0] == 0:
            return # no selection 
        items_df_index = items_df_line.index[0]
        current_active_status = items_df.iloc[items_df_index]['active']
        selection_index = items_listbox.curselection()[0]

        # currently not active
        if current_active_status == 0: 
            # change the active status in df
            items_df.at[items_df_index, 'active'] = 1
            # black in the selection 
            items_listbox.itemconfig(selection_index, fg="black")

        # currently active
        else:
            # change the active status in df
            items_df.at[items_df_index, 'active'] = 0
            # grey out the selection
            items_listbox.itemconfig(selection_index, fg="gray")
        
    def edit_items_save():
        # get items in the listbox
        item_new_order = list(items_listbox.get(0, END))
        if item_new_order:            
            # remove the old order
            items_df.drop('order', inplace = True, axis = 1)
            # use merge to replace with the new order
            new_order = list(range(1, len(item_new_order) + 1))
            new_order_df = pd.DataFrame({item_eng: item_new_order, 'order': new_order})
            merged_df = items_df.merge(new_order_df, on = item_eng)
            # save 
            merged_df.to_csv(cwd + f"{item_eng}s.csv", index = False)

        # return to main page
        edit_items_frame.destroy()
        main_page(root)

    delete_btn = Button(new_items_btns_frame, text = "删除", command = item_delete, font=("微软雅黑", 16))
    delete_btn.grid(row = 1, column = 0, padx = 20, pady = 10)
    on_off_btn = Button(new_items_btns_frame, text = "隐藏/显示", command = item_on_off, font=("微软雅黑", 16))
    on_off_btn.grid(row = 1, column = 1, padx = 20, pady = 10)
    save_btn = Button(new_items_btns_frame, text = "保存并返回主页", command = edit_items_save, font=("微软雅黑", 16))
    save_btn.grid(row = 1, column = 2, padx = 20, pady = 10)
    
    new_items_btns_frame.pack()
    
    edit_items_frame.pack()

def pending_payments_page(root):

    ### VIEW 1.5: pending payments
    page_frame = Frame(root)

    # title
    title = Label(page_frame, text = "待结款项", font=("微软雅黑", 32))
    title.pack()

    # read in dfs
    works_df = pd.read_csv(cwd + "works.csv")
    status_log_df = pd.read_csv(cwd + "status_log.csv", parse_dates = [3, 4, 5], date_parser = pd.to_datetime)
    clients_df = pd.read_csv(cwd + "clients.csv")
    status_df = pd.read_csv(cwd + "status.csv")

    # create a frame for canvas
    canvas_frame = Frame(page_frame)
    # create a canvas
    canvas = Canvas(canvas_frame)
    canvas.grid(row = 0, column = 0, sticky="nsew")
    
    # add scrollbars to the canvas
    canvas_y_scrollbar = ttk.Scrollbar(canvas_frame, orient = VERTICAL, command = canvas.yview)
    canvas_y_scrollbar.grid(row=0, column=1, sticky="ns")
    canvas_x_scrollbar = ttk.Scrollbar(canvas_frame, orient = HORIZONTAL, command = canvas.xview)
    canvas_x_scrollbar.grid(row=1, column=0, sticky="ew")

    # configure the canvas
    canvas.configure(yscrollcommand = canvas_y_scrollbar.set)
    canvas.configure(xscrollcommand = canvas_x_scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox('all')))

    # table contents
    table_frame = Frame(canvas)

    # add table_frame onto canvas
    canvas.create_window((0, 0), window = table_frame, anchor = 'nw')

    def construct_pending_payments(df):

        # remove current widgets
        for widget in table_frame.winfo_children():
            widget.destroy()

        # headers
        header_name = Label(table_frame, text = "作品名", font=("微软雅黑", 16))
        header_client = Label(table_frame, text = "客户名", font=("微软雅黑", 16))
        header_status = Label(table_frame, text = "状态", font=("微软雅黑", 16))
        header_end_date = Label(table_frame, text = "已收", font=("微软雅黑", 16))
        header_memo = Label(table_frame, text = "待付", font=("微软雅黑", 16))
        # grid the headers
        header_name.grid(row = 0, column = 0, padx = 20, pady = 10)
        header_client.grid(row = 0, column = 1, padx = 20, pady = 10)
        header_status.grid(row = 0, column = 2, padx = 20, pady = 10)
        header_end_date.grid(row = 0, column = 3, padx = 20, pady = 10)
        header_memo.grid(row = 0, column = 4, padx = 20, pady = 10)

        # for each active work, show on the view
        def work_details(work_id):
            page_frame.destroy()
            details_page(root, work_id, pending_payments_page)

        # list the works
        total = 0
        df = df.reset_index()
        for i, row in df.iterrows():
            # calculate the paid/due amount
            if row['deposited'] == 0:
                paid_amount = 0
                due_amount = row['price']
            else:
                paid_amount = row['deposit']
                due_amount = row['price'] - row['deposit']
            # keep track of total due
            total += due_amount
            # show the work details
            active_work_i_btn = Button(table_frame, text = row['name'], command= lambda row = row: work_details(row['work_id']), font=("微软雅黑", 16))
            active_work_i_client = Label(table_frame, text = row['client'], font=("微软雅黑", 16))
            active_work_i_status = Label(table_frame, text = row['status'], font=("微软雅黑", 16))
            active_work_i_end_date = Label(table_frame, text = paid_amount, font=("微软雅黑", 16))
            active_work_i_memo = Label(table_frame, text = due_amount, font=("微软雅黑", 16))
            # grid the details
            active_work_i_btn.grid(row = i + 1, column = 0, padx = 20, pady = 10)
            active_work_i_client.grid(row = i + 1, column = 1, padx = 20, pady = 10)
            active_work_i_status.grid(row = i + 1, column = 2, padx = 20, pady = 10)
            active_work_i_end_date.grid(row = i + 1, column = 3, padx = 20, pady = 10)
            active_work_i_memo.grid(row = i + 1, column = 4, padx = 20, pady = 10)

        # total
        total_row = df.shape[0] + 1
        total_label = Label(table_frame, text = "总计：", font=("微软雅黑", 16))
        total_label.grid(row = total_row, column = 3)
        total_amt = Label(table_frame, text = total, font=("微软雅黑", 16))
        total_amt.grid(row = total_row, column = 4)

        # table_frame.pack() 
        canvas_frame.pack()
        table_frame.update()
        frame_width = table_frame.winfo_width()
        frame_height = table_frame.winfo_height()
        canvas.configure(width = min(frame_width, 1600), height = min(850, frame_height))

    # dfs to show
    # not fully paid
    df = works_df[works_df['fully_paid'] == 0][['id', 'name', 'client_id', 'deposit', 'price', 'deposited', 'fully_paid']].rename(columns = {'id': 'work_id'})
    # get client names
    df = df.merge(clients_df[['id', 'client']], left_on = "client_id", right_on = "id", suffixes=('_work', '_client')).drop('id', axis = 1) # drop repetitive client id
    # get latest log for each work
    status_log_df['rank'] = status_log_df.groupby('work_id')['timestamp'].rank(ascending = False)
    latest_logs = status_log_df[status_log_df['rank'] == 1]
    status_log_df.drop('rank', axis = 1, inplace = True)
    # get latest status name for each work that's not fully paid
    df = df.merge(latest_logs[['work_id', 'status_id']], on = "work_id")
    df = df.merge(status_df, left_on = 'status_id', right_on = 'id').drop('id', axis = 1) # drop repetitive status id

    def filter_records(_):
        select_client = filter_dropdown.get()
        if select_client: # when not selected, show all 
            filtered_df = df[df['client'] == filter_dropdown.get()]
            construct_pending_payments(filtered_df)  
            return_btn.focus()

    # filter by clients
    filter_frame = Frame(page_frame)
    filter_label = Label(filter_frame, text = "按客户筛选：", font=("微软雅黑", 16))
    filter_label.grid(row = 0, column = 0)
    clients_list = get_client_list()
    filter_dropdown = ttk.Combobox(filter_frame, value = clients_list, font=("微软雅黑", 16), state="readonly")
    filter_dropdown.bind("<<ComboboxSelected>>", filter_records)
    filter_dropdown.grid(row = 0, column = 1)
    def cancel_filter():
        filter_dropdown.set('')
        construct_pending_payments(df)
        filter_cancel_btn.focus()
    filter_cancel_btn = Button(filter_frame, text = "取消", command = cancel_filter, font=("微软雅黑", 16))
    filter_cancel_btn.grid(row = 0, column = 2)
    filter_frame.pack()

    # construct list
    construct_pending_payments(df)

    # return button
    def return_to_main_page():
        page_frame.destroy()
        main_page(root)

    return_btn = Button(page_frame, text = "返回", command = return_to_main_page, font=("微软雅黑", 16))
    return_btn.pack()

    page_frame.pack()

def all_works_page(root):
    
    ### VIEW 1.6: all works
    page_frame = Frame(root)

    # title
    title = Label(page_frame, text = "工作总览", font=("微软雅黑", 32))
    title.pack()

    # read in dfs
    works_df = pd.read_csv(cwd + "works.csv")
    status_log_df = pd.read_csv(cwd + "status_log.csv", parse_dates = [3, 4, 5], date_parser = pd.to_datetime)
    clients_df = pd.read_csv(cwd + "clients.csv")
    status_df = pd.read_csv(cwd + "status.csv")

    # create a frame for canvas
    canvas_frame = Frame(page_frame)
    # create a canvas
    canvas = Canvas(canvas_frame)
    canvas.grid(row = 0, column = 0, sticky="nsew")
    
    # add scrollbars to the canvas
    canvas_y_scrollbar = ttk.Scrollbar(canvas_frame, orient = VERTICAL, command = canvas.yview)
    canvas_y_scrollbar.grid(row=0, column=1, sticky="ns")
    canvas_x_scrollbar = ttk.Scrollbar(canvas_frame, orient = HORIZONTAL, command = canvas.xview)
    canvas_x_scrollbar.grid(row=1, column=0, sticky="ew")

    # configure the canvas
    canvas.configure(yscrollcommand = canvas_y_scrollbar.set)
    canvas.configure(xscrollcommand = canvas_x_scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox('all')))

    # table contents
    table_frame = Frame(canvas)

    # add table_frame onto canvas
    canvas.create_window((0, 0), window = table_frame, anchor = 'nw')

    # headers
    header_name = Label(table_frame, text = "作品名", font=("微软雅黑", 16))
    header_client = Label(table_frame, text = "客户名", font=("微软雅黑", 16))
    header_status = Label(table_frame, text = "状态", font=("微软雅黑", 16))
    header_end_date = Label(table_frame, text = "截止日期", font=("微软雅黑", 16))
    header_memo = Label(table_frame, text = "备注", font=("微软雅黑", 16))
    # grid the headers
    header_name.grid(row = 0, column = 0, padx = 20, pady = 10)
    header_client.grid(row = 0, column = 1, padx = 20, pady = 10)
    header_status.grid(row = 0, column = 2, padx = 20, pady = 10)
    header_end_date.grid(row = 0, column = 3, padx = 20, pady = 10)
    header_memo.grid(row = 0, column = 4, padx = 20, pady = 10, sticky = 'w')

    # separator line
    separator = ttk.Separator(table_frame, orient='horizontal')
    separator.grid(row = 1, column = 0, columnspan = 5, sticky="ew")

    # dfs to show
    # active works
    df = works_df[['id', 'name', 'client_id', 'memo']].rename(columns = {'id': 'work_id'}).fillna('')
    # get client names
    df = df.merge(clients_df[['id', 'client']], left_on = "client_id", right_on = "id", suffixes=('_work', '_client')).drop('id', axis = 1) # drop repetitive client id
    # get latest log for each work
    status_log_df['rank'] = status_log_df.groupby('work_id')['timestamp'].rank(ascending = False)
    latest_logs = status_log_df[status_log_df['rank'] == 1]
    status_log_df.drop('rank', axis = 1, inplace = True)
    # get latest status name for each work that's not fully paid
    df = df.merge(latest_logs[['work_id', 'status_id', 'end_date']], on = "work_id")
    df = df.merge(status_df, left_on = 'status_id', right_on = 'id').drop('id', axis = 1) # drop repetitive status id
    # separate the active/inactive ones
    active_df = df[~df['status_id'].isin((4, 5))].sort_values(by = "end_date").reset_index()
    active_rows = active_df.shape[0]
    inactive_df = df[df['status_id'].isin((4, 5))].sort_values(by = "end_date").reset_index()

    # for each active work, show on the view
    def work_details(work_id):
        page_frame.destroy()
        details_page(root, work_id,all_works_page)
    def construct_work_table(df, starting_row):
        for i, row in df.iterrows():
            # show the work details
            active_work_i_btn = Button(table_frame, text = row['name'], command= lambda row = row: work_details(row['work_id']), font=("微软雅黑", 16))
            active_work_i_client = Label(table_frame, text = row['client'], font=("微软雅黑", 16))
            active_work_i_status = Label(table_frame, text = row['status'], font=("微软雅黑", 16))
            active_work_i_end_date = Label(table_frame, text = row['end_date'].date(), font=("微软雅黑", 16))
            active_work_i_memo = Label(table_frame, text = row['memo'], font=("微软雅黑", 16))
            # grid the details
            active_work_i_btn.grid(row = i + starting_row, column = 0, padx = 20, pady = 10)
            active_work_i_client.grid(row = i + starting_row, column = 1, padx = 20, pady = 10)
            active_work_i_status.grid(row = i + starting_row, column = 2, padx = 20, pady = 10)
            active_work_i_end_date.grid(row = i + starting_row, column = 3, padx = 20, pady = 10)
            active_work_i_memo.grid(row = i + starting_row, column = 4, padx = 20, pady = 10, sticky = 'w')

    # list the active works
    construct_work_table(active_df, 2)  

    # separator line
    # separator = ttk.Separator(table_frame, orient='horizontal')
    # separator.grid(row = 2 + active_rows + 1, column = 0, columnspan = 5, sticky="ew")
    separator2 = Frame(table_frame, bd=10, relief='sunken', height=4)
    separator2.grid(row = 2 + active_rows + 1, column = 0, columnspan = 5, sticky="ew")

    # list inactive works
    construct_work_table(inactive_df, 2 + active_rows + 2)  

    # table_frame.pack() 
    canvas_frame.pack()
    table_frame.update()
    frame_width = table_frame.winfo_width()
    canvas.configure(width = min(frame_width, 1600), height = 550)


    # return button
    def return_to_main_page():
        page_frame.destroy()
        main_page(root)

    return_btn = Button(page_frame, text = "返回", command = return_to_main_page, font=("微软雅黑", 16))
    return_btn.pack()

    page_frame.pack()