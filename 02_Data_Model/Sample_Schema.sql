// Pseudocode: Fact_Financials Table

DEFINE TABLE Fact_Financials:
    Columns:
        - DateKey : Integer
        - Amount  : Decimal(18,2)

    Relationships:
        - DateKey references Dim_Date.DateKey (FK)

    Purpose:
        - Store financial transaction amounts by date
