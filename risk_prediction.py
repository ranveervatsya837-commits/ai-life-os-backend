class RiskPredictionEngine:

    @staticmethod
    def calculate(patient, records):

        risk_score = 0
        risks = []

        age = patient["age"]

        if age >= 60:
            risk_score += 20
            risks.append("Senior Age")

        for record in records:

            diagnosis = str(
                record["diagnosis"]
            ).lower()

            if "diabetes" in diagnosis:
                risk_score += 30
                risks.append("Diabetes")

            elif "hypertension" in diagnosis:
                risk_score += 25
                risks.append("Hypertension")

            elif "heart" in diagnosis:
                risk_score += 35
                risks.append("Heart Disease")

            elif "viral" in diagnosis:
                risk_score += 10
                risks.append("Viral Infection")

            elif "fever" in diagnosis:
                risk_score += 5
                risks.append("Fever")

        risk_score = min(risk_score, 100)

        if risk_score >= 70:
            level = "High"
        elif risk_score >= 40:
            level = "Medium"
        else:
            level = "Low"

        return {
            "risk_score": risk_score,
            "risk_level": level,
            "risk_factors": list(set(risks))
        }