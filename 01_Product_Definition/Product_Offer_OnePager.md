// Pseudocode: Vantix SME Dashboard Pricing - Complete Implementation

// === MAIN PRODUCT SYSTEM ===
APP "Vantix_SME_Dashboard_Pricing" {
    
    // === PRODUCT DEFINITION ===
    CLASS Product {
        NAME = "Vantix SME Dashboard"
        VERSION = "1.0"
        CATEGORY = "Business Intelligence Dashboard"
        TARGET_MARKET = "South African SMEs"
        INDUSTRY = "Agriculture"
    }

    // === PRICING MODEL DEFINITION ===
    CLASS PricingModel {
        SETUP_FEE = R10000
        MONTHLY_FEE = R2000
        CURRENCY = "ZAR"
        
        // === PRICE CALCULATION FUNCTIONS ===
        FUNCTION CalculateSetupFee(client_size):
            IF (client_size == "Small") {
                RETURN SETUP_FEE * 0.9 // 10% discount for small clients
            } ELSE IF (client_size == "Medium") {
                RETURN SETUP_FEE
            } ELSE {
                RETURN SETUP_FEE * 1.2 // 20% premium for large clients
            }
        
        FUNCTION CalculateMonthlyFee(client_size):
            IF (client_size == "Small") {
                RETURN MONTHLY_FEE * 0.8 // 20% discount for small clients
            } ELSE IF (client_size == "Medium") {
                RETURN MONTHLY_FEE
            } ELSE {
                RETURN MONTHLY_FEE * 1.1 // 10% premium for large clients
            }
    }

    // === CONTRACT TERMS ===
    CLASS ContractTerms {
        SETUP_FEE_ONCE_OFF = TRUE
        MONTHLY_FEE_RECURRING = TRUE
        
        INCLUDED_SERVICES = [
            "Standard dashboard",
            "Ongoing refresh + monitoring",
            "Basic support",
            "Template access",
            "Measures library access"
        ]
        
        IP_RETENTION = {
            "template": "Vantix retains ownership",
            "measures_library": "Vantix retains ownership",
            "customizations": "Client owns customizations"
        }
        
        CLIENT_OWNERSHIP = {
            "data": "Client owns their data",
            "tenant": "Client owns their tenant",
            "custom_dashboards": "Client owns custom dashboards"
        }
        
        // === CONTRACT VALIDATION ===
        FUNCTION ValidateContractTerms(contract_details):
            RETURN {
                setup_fee_valid: contract_details.setup_fee == SETUP_FEE,
                monthly_fee_valid: contract_details.monthly_fee == MONTHLY_FEE,
                services_included: contract_details.services IN INCLUDED_SERVICES,
                ip_retention_valid: contract_details.ip_retention == IP_RETENTION,
                client_ownership_valid: contract_details.client_ownership == CLIENT_OWNERSHIP
            }
    }

    // === CLIENT SEGMENTATION ===
    CLASS ClientSegmentation {
        FUNCTION SegmentClient(client_profile):
            IF (client_profile.employees < 10 AND client_profile.revenue < R500000) {
                RETURN "Small"
            } ELSE IF (client_profile.employees BETWEEN 10 AND 50 AND client_profile.revenue BETWEEN R500000 AND R2000000) {
                RETURN "Medium"
            } ELSE {
                RETURN "Large"
            }
        
        FUNCTION GetClientTier(client_segment):
            SWITCH(client_segment) {
                CASE "Small":
                    RETURN "Tier1"
                CASE "Medium":
                    RETURN "Tier2"
                CASE "Large":
                    RETURN "Tier3"
            }
    }

    // === PRICE CALCULATION ENGINE ===
    FUNCTION CalculateTotalPrice(client_profile, contract_duration_months, additional_services):
        // Segment client
        client_segment = ClientSegmentation.SegmentClient(client_profile)
        
        // Calculate base pricing
        setup_fee = PricingModel.CalculateSetupFee(client_segment)
        monthly_fee = PricingModel.CalculateMonthlyFee(client_segment)
        
        // Calculate total
        total_setup = setup_fee
        total_monthly = monthly_fee * contract_duration_months
        
        // Add additional services
        additional_cost = 0
        FOREACH(service IN additional_services) {
            additional_cost += CalculateServiceCost(service)
        }
        
        total_cost = total_setup + total_monthly + additional_cost
        
        RETURN {
            client_segment: client_segment,
            setup_fee: setup_fee,
            monthly_fee: monthly_fee,
            contract_duration: contract_duration_months,
            additional_services_cost: additional_cost,
            total_cost: total_cost,
            currency: "ZAR"
        }

    // === SERVICE COST CALCULATION ===
    FUNCTION CalculateServiceCost(service):
        SERVICE_COSTS = {
            "data_warehouse_setup": R3000,
            "custom_reporting": R1500,
            "advanced_analytics": R2500,
            "user_training": R800,
            "priority_support": R500
        }
        
        RETURN SERVICE_COSTS[service] OR R0

    // === CONTRACT GENERATION ===
    FUNCTION GenerateContract(client_profile, contract_duration_months, additional_services):
        pricing = CalculateTotalPrice(client_profile, contract_duration_months, additional_services)
        
        contract = {
            product: Product.NAME,
            version: Product.VERSION,
            client_name: client_profile.name,
            client_segment: pricing.client_segment,
            pricing: pricing,
            contract_terms: ContractTerms,
            additional_services: additional_services,
            contract_start_date: GetCurrentDate(),
            contract_end_date: CalculateEndDate(contract_duration_months),
            signature_required: TRUE,
            ip_protection: "High"
        }
        
        RETURN contract

    // === DATE CALCULATION ===
    FUNCTION CalculateEndDate(months):
        current_date = GetCurrentDate()
        end_date = AddMonths(current_date, months)
        RETURN end_date

    // === PROTECTION LEVELS ===
    CLASS ProtectionLevels {
        IP_PROTECTION = "High"
        TIME_PROTECTION = "High"
        CLIENT_PROTECTION = "Medium"
        
        FUNCTION GetProtectionSummary():
            RETURN {
                ip_protection: IP_PROTECTION,
                time_protection: TIME_PROTECTION,
                client_protection: CLIENT_PROTECTION,
                benefits: [
                    "Template and measures library ownership retained",
                    "Client data and tenant ownership",
                    "Clear contract terms",
                    "Standard support included"
                ]
            }
    }

    // === MAIN EXECUTION FLOW ===
    MAIN {
        // 1. Client profile collected
        client_profile = getClientProfile()
        
        // 2. Contract duration
        contract_duration_months = getContractDuration()
        
        // 3. Additional services
        additional_services = getAdditionalServices()
        
        // 4. Generate contract
        contract = GenerateContract(client_profile, contract_duration_months, additional_services)
        
        // 5. Validate contract
        validation = ContractTerms.ValidateContractTerms(contract)
        
        // 6. Protection summary
        protection = ProtectionLevels.GetProtectionSummary()
        
        // 7. Return final pricing package
        RETURN {
            product: Product.NAME,
            contract: contract,
            validation: validation,
            protection: protection,
            pricing_summary: {
                setup_fee: contract.pricing.setup_fee,
                monthly_fee: contract.pricing.monthly_fee,
                total_cost: contract.pricing.total_cost,
                currency: contract.pricing.currency
            }
        }
    }
}
