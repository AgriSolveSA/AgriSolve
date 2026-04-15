// Pseudocode: Pricing Tiers (Client Picks) - Complete Implementation

// === MAIN PRICING SYSTEM ===
APP "Vantix_Pricing_Tiers" {
    
    // === PRICING TIER DEFINITIONS ===
    CLASS PricingTiers {
        
        // Tier 1: Starter Managed Service
        FUNCTION Tier1_StarterManaged():
            RETURN {
                tier_name: "Starter Managed",
                client_segment: "Price-sensitive SMEs",
                goal: "Fast acceptance + reference",
                setup_fee: RANDOM_RANGE(R5000, R7500),
                monthly_fee: RANDOM_RANGE(R1500, R2500),
                minimum_term: 3, // months
                included_features: [
                    "Standard dashboard",
                    "Refresh monitoring",
                    "Monthly PDF pack",
                    "1 small change per month"
                ],
                excluded_features: [
                    "New data sources",
                    "New pages",
                    "Bespoke analytics"
                ],
                target_market: "Small businesses with basic needs",
                risk_level: "LOW"
            }
        
        // Tier 2: Standard Managed Service
        FUNCTION Tier2_StandardManaged():
            RETURN {
                tier_name: "Standard Managed",
                client_segment: "Most SMEs",
                goal: "Balance income + support load",
                setup_fee: RANDOM_RANGE(R10000, R15000),
                monthly_fee: RANDOM_RANGE(R2500, R4500),
                minimum_term: RANDOM_RANGE(6, 12), // months
                included_features: [
                    "Standard dashboard",
                    "Refresh monitoring",
                    "Monthly PDF pack",
                    "Exceptions handling",
                    "2 small changes per month"
                ],
                excluded_features: [
                    "New data sources",
                    "New pages",
                    "Bespoke analytics"
                ],
                target_market: "Growing SMEs with moderate needs",
                risk_level: "MEDIUM"
            }
        
        // Tier 3: Ownership Buy-Out
        FUNCTION Tier3_OwnershipBuyOut():
            RETURN {
                tier_name: "Ownership Buy-Out",
                client_segment: "Clients who refuse retainers",
                goal: "Full ownership / hand-over",
                once_off_fee: RANDOM_RANGE(R45000, R120000),
                optional_support: {
                    monthly_fee: RANDOM_RANGE(R1500, R3000),
                    hourly_blocks: "Prepaid hourly rates"
                },
                included_features: [
                    "PBIX files",
                    "Data model",
                    "Deployment instructions",
                    "Handover session",
                    "Documentation"
                ],
                excluded_features: [
                    "Managed refresh monitoring",
                    "Ongoing support (unless opted-in)"
                ],
                target_market: "Larger SMEs or clients requiring full control",
                risk_level: "HIGH"
            }
    }

    // === SCOPE GUARDRAIL SYSTEM ===
    CLASS ScopeGuardrail {
        
        FUNCTION ValidateClientRequest(client_request, current_tier):
            // Check if request is outside standard package
            IF (client_request IN current_tier.excluded_features) {
                // Apply guardrail rules
                RETURN {
                    action_required: TRUE,
                    options: [
                        "Quote separately",
                        "Move client to higher tier",
                        "Decline politely"
                    ],
                    recommended_option: "Quote separately",
                    reason: "Request exceeds tier scope"
                }
            } ELSE {
                RETURN {
                    action_required: FALSE,
                    message: "Request within scope"
                }
            }
        
        // === SCOPE VALIDATION LOGIC ===
        FUNCTION ApplyScopeValidation(client_request, selected_tier):
            SWITCH(selected_tier) {
                CASE "Tier1":
                    IF (client_request IN Tier1.excluded_features) {
                        RETURN handleTier1ScopeViolation(client_request)
                    }
                    BREAK
                
                CASE "Tier2":
                    IF (client_request IN Tier2.excluded_features) {
                        RETURN handleTier2ScopeViolation(client_request)
                    }
                    BREAK
                
                CASE "Tier3":
                    IF (client_request IN Tier3.excluded_features) {
                        RETURN handleTier3ScopeViolation(client_request)
                    }
                    BREAK
            }
    }

    // === SCOPE VIOLATION HANDLERS ===
    FUNCTION handleTier1ScopeViolation(request):
        RETURN {
            response: "Quote separately",
            additional_cost: calculateAdditionalCost(request),
            explanation: "Tier 1 is limited to basic features",
            alternative: "Upgrade to Tier 2 or Tier 3"
        }

    FUNCTION handleTier2ScopeViolation(request):
        RETURN {
            response: "Move to higher tier",
            tier_upgrade: "Tier3_OwnershipBuyOut",
            cost_estimate: calculateTier3Cost(),
            explanation: "Request exceeds Tier 2 capabilities",
            benefit: "Full ownership and advanced features"
        }

    FUNCTION handleTier3ScopeViolation(request):
        RETURN {
            response: "Decline politely",
            reason: "Request is outside scope of ownership buy-out",
            alternative: "Consider custom development",
            explanation: "Tier 3 is already comprehensive"
        }

    // === COST CALCULATION FUNCTIONS ===
    FUNCTION calculateAdditionalCost(request):
        BASE_COSTS = {
            "New data sources": R2000,
            "New pages": R1500,
            "Bespoke analytics": R3000
        }
        RETURN BASE_COSTS[request] OR R1000

    FUNCTION calculateTier3Cost():
        RETURN RANDOM_RANGE(R45000, R120000)

    // === CLIENT SEGMENTATION ===
    CLASS ClientSegmentation {
        
        FUNCTION IdentifyClientType(client_profile):
            IF (client_profile.budget < R10000) {
                RETURN "Tier1_Starter"
            } ELSE IF (client_profile.budget BETWEEN R10000 AND R30000) {
                RETURN "Tier2_Standard"
            } ELSE {
                RETURN "Tier3_Ownership"
            }
        
        FUNCTION GetRecommendedTier(client_profile):
            RETURN IdentifyClientType(client_profile)
    }

    // === PRICING CALCULATOR ===
    FUNCTION CalculateTotalCost(tier, duration_months, additional_services):
        total_cost = 0
        
        IF (tier == "Tier1") {
            total_cost = tier.setup_fee + (tier.monthly_fee * duration_months)
        } ELSE IF (tier == "Tier2") {
            total_cost = tier.setup_fee + (tier.monthly_fee * duration_months)
        } ELSE IF (tier == "Tier3") {
            total_cost = tier.once_off_fee
            IF (additional_services.includes("support")) {
                total_cost += (tier.optional_support.monthly_fee * duration_months)
            }
        }
        
        // Add additional services
        FOREACH(service IN additional_services) {
            total_cost += calculateAdditionalCost(service)
        }
        
        RETURN total_cost

    // === MAIN EXECUTION FLOW ===
    MAIN {
        // 1. Client profile collected
        client_profile = getClientProfile()
        
        // 2. Client segmentation
        recommended_tier = ClientSegmentation.GetRecommendedTier(client_profile)
        
        // 3. Tier selection
        selected_tier = PricingTiers[recommended_tier]()
        
        // 4. Duration and additional services
        duration_months = getContractDuration()
        additional_services = getAdditionalServices()
        
        // 5. Cost calculation
        total_cost = CalculateTotalCost(selected_tier, duration_months, additional_services)
        
        // 6. Scope validation
        scope_validation = ScopeGuardrail.ValidateClientRequest(additional_services, selected_tier)
        
        // 7. Final pricing recommendation
        RETURN {
            recommended_tier: selected_tier,
            pricing_summary: {
                setup_fee: selected_tier.setup_fee,
                monthly_fee: selected_tier.monthly_fee,
                total_cost: total_cost,
                duration: duration_months
            },
            scope_validation: scope_validation,
            client_segment: client_profile.segment,
            protection_level: "High" // IP and time protection
        }
    }
}
