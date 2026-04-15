// Pseudocode: Schema Change Checklist (Client Communication)

DEFINE ClientChecklist_BeforeExportChange:
    Step1: IdentifyChange
        - ColumnNamesChanged?
        - ColumnTypesChanged?
        - NewColumnsAdded?
        - ColumnsRemoved?
    Step2: ConfirmEffectiveDate
        - When does change take effect?
    Step3: ProvideSamples
        - File1 = LastMonthExport
        - File2 = NewMonthExport
    Step4: ConfirmBusinessMeaning
        - Explain meaning of any changed fields

DEFINE VantixResponse:
    Step1: ClassifyChange
        - IF SmallChangeInScope → Proceed
        - ELSE → OutOfScopeQuote
    Step2: UpdatePowerQueryStepsSafely
        - Apply schema adjustments
        - Validate refresh stability
