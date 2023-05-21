from datetime import date

class Controller:
    def __init__(self, model, view):
        self.view = view
        self.model = model
        self.view.start_scheduler(0,1)
        self.view.attach2controller(self)
        self.model.create_tables()
        # print('1:',self.model.steps)
        temp = self.model.load_steps()
        # print('2:',self.model.steps)
        # print('>> data read:', temp)
        self.view.set_data(temp)
        self.view.update_ratio()

    def date_change(self):
        print('>> date_change')
        stopped = self.view.date_change()
        self.model.save_records()
        self.model.date_change()
        # temp = self.model.load_steps()
        # print(temp)
        # self.view.set_data(temp) #
        self.view.date_changed(stopped)

    
    def add_task(self):
        # print('>> add_task')
        task_name = self.view.get_new_task_name()
        if self.model.exist_task(task_name):
            self.view.msg_window("Existed", "The task existed", warning=True)
        elif task_name == '':
            self.view.msg_window("Empty name", "The task name shouldn't be empty", warning=True)
        else:
            self.model.add_task(task_name)
            self.view.add_task_recorder(task_name)
    
    def remove_task(self):
        # print('>> remove_task')
        remove = self.view.remove_task()
        self.model.remove_task(remove)
    
    def clear_tasks(self):
        # print('>> clear_tasks')
        self.view.clear_tasks()
        self.model.clear_all()
    
    def save_records(self):
        # print('>> save_records')
        self.model.save_records()
        self.view.saved()
    
    def load_combobox(self):
        # print('>> load_combobox')
        tasks = self.model.get_tasks()
        # print(tasks)
        self.view.combobox_load_tasks(tasks)
    
    def show_records(self):
        # print('>> show_records')
        tasks = self.view.get_combobox_selected()
        if len(tasks) > 0:
            (table_data, date_total) = self.model.get_table_data(tasks)
            self.view.show_records(tasks, table_data, date_total)