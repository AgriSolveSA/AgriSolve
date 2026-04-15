// Pseudocode: Power Query Templates (Starter)

TEMPLATE A: LoadMonthlyExcelExportFromFolder
    Assumptions:
        - Files named GL_YYYYMM.xlsx in folder
    Steps:
        1. Define FolderPath
        2. Source = Folder.Files(FolderPath)
        3. Filtered = Select rows where Name starts "GL_" and Extension = ".xlsx"
        4. AddedYM = Add column YYYYMM from filename
        5. Latest = Sort by YYYYMM descending, take first Content
        6. Excel = Excel.Workbook(Latest, true)
        7. Sheet = Select "Sheet1"
        8. Promoted = Promote headers
        9. Typed = Transform column types (Date, Account, Amount)
    Output = Typed table

TEMPLATE B: DefensiveCSVLoader
    Assumptions:
        - File named AR_YYYYMM.csv
    Steps:
        1. Source = Csv.Document(File.Contents(path), delimiter=",", encoding=65001)
        2. Promoted = Promote headers
        3. Keep = Select columns {Customer, InvoiceDate, DueDate, Balance, AgeBucket}, allow missing fields
        4. Typed = Transform column types (InvoiceDate=date, DueDate=date, Balance=number, AgeBucket=text)
    Output = Typed table
