import json
from openpyxl_templates.table_sheet import TableSheet
from openpyxl_templates import TemplatedWorkbook, TemplatedWorksheet
from openpyxl_templates.table_sheet.columns import CharColumn, IntColumn, FloatColumn


class DictSheet(TemplatedWorksheet):
    def write(self, data):
        worksheet = self.worksheet

        for item in data.items():
            worksheet.append(list(item))

    def read(self):
        worksheet = self.worksheet
        data = {}

        for row in worksheet.rows:
            data[row[0].value] = row[1].value

        return data
    
class MobileSheet(TableSheet):
   full_name_of_the_product = CharColumn()
   color = CharColumn()
   memory_size = IntColumn()
   seller = CharColumn()
   regular_price = IntColumn()
   promotional_price_= IntColumn()
   all_product_photos = CharColumn()
   product_code = IntColumn()
   number_of_reviews = IntColumn()
   series = CharColumn()
   screen_diagonal = CharColumn()
   display_resolution = CharColumn()
   product_specifications = CharColumn()

class MobileRozetkaWorkbook(TemplatedWorkbook):
   mobile = MobileSheet()

m = MobileRozetkaWorkbook()
def save_to_exel(data,name):
    m.mobile.write(objects=(
        (
            data["full_name_of_the_product"],
            data["color"],
            data["memory_size"],
            data["seller"],
            data["regular_price"],
            data["promotional_price"],
            ", ".join(data["all_product_photos"]),
            data["product_code"],
            data["number_of_reviews"],
            data["series"],
            data["screen_diagonal"],
            data["display_resolution"],
            json.dumps(data['product_specifications'], ensure_ascii=False) 
        ),
    ))

    m.save(f"C:/Users/Admin/projects/rozetkacomua_project/results/{name}.xlsx")

# save_to_exel(data,"test")