import pandas as pd
import numpy as np
from xlsxwriter.utility import xl_rowcol_to_cell

df = pd.read_excel ("excel-comp-datav2.xlsx")
df.head ( )

number_rows = len (df.index)
#print (number_rows)

# increase the salary by 10 %
#example = df.assign(Revised_Salary = lambda x: df['Feb'] + df['Mar']/2)

# Add some summary data using the new assign functionality in pandas 0.16
df = df.assign (total = df['Jan'] + df['Feb'] + df['Mar'])
df.head()
print(df)

df = df.assign(quota_pct=(1+(df['total'] - df['quota'])/df['quota']))
df.head()

writer_orig = pd.ExcelWriter('simple.xlsx', engine='xlsxwriter')
df.to_excel(writer_orig, index=False, sheet_name='report')
writer_orig.save()

writer = pd.ExcelWriter('fancy.xlsx', engine='xlsxwriter')
df.to_excel(writer, index=False, sheet_name='report')
workbook = writer.book
worksheet = writer.sheets['report']
worksheet.set_zoom(90)

# Add a number format for cells with money.
money_fmt = workbook.add_format({'num_format': '$#,##0', 'bold': True})

# Add a percent format with 1 decimal point
percent_fmt = workbook.add_format({'num_format': '0.0%', 'bold': True})

# Total formatting
total_fmt = workbook.add_format({'align': 'right', 'num_format': '$#,##0','bold': True, 'bottom':6})
# Total percent format
total_percent_fmt = workbook.add_format({'align': 'right', 'num_format': '0.0%','bold': True, 'bottom':6})

# Account info columns
worksheet.set_column('B:D', 20)
# State column
worksheet.set_column('E:E', 5)
# Post code
worksheet.set_column('F:F', 10)

# Monthly columns
worksheet.set_column('G:K', 12, money_fmt)
# Quota percent columns
worksheet.set_column('L:L', 12, percent_fmt)

# Add total rows
for column in range(6, 11):
    # Determine where we will place the formula
    cell_location = xl_rowcol_to_cell(number_rows+1, column)
    # Get the range to use for the sum formula
    start_range = xl_rowcol_to_cell(1, column)
    end_range = xl_rowcol_to_cell(number_rows, column)
    # Construct and write the formula
    formula = "=SUM({:s}:{:s})".format(start_range, end_range)
    worksheet.write_formula(cell_location, formula, total_fmt)

# Add a total label
worksheet.write_string(number_rows+1, 5, "Total",total_fmt)
percent_formula = "=1+(K{0}-G{0})/G{0}".format(number_rows+2)
worksheet.write_formula(number_rows+1, 11, percent_formula, total_percent_fmt)

# Define our range for the color formatting
color_range = "L2:L{}".format(number_rows+1)

# Add a format. Light red fill with dark red text.
format1 = workbook.add_format({'bg_color': '#FFC7CE','font_color': '#9C0006'})

# Add a format. Green fill with dark green text.
format2 = workbook.add_format({'bg_color': '#C6EFCE','font_color': '#006100'})

# Highlight the top 5 values in Green
worksheet.conditional_format(color_range, {'type': 'top','value': '5','format': format2})

# Highlight the bottom 5 values in Red
worksheet.conditional_format(color_range, {'type': 'bottom','value': '5','format': format1})
writer.save()
