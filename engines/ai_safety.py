class AISafetyLayer:

    def __init__(self, user):
        self.user = user

    def run_safety_checks(self):

        issues = []

        age = int(self.user.age)
        if age <= 0 or age > 120:
            issues.append("Invalid Age")

        if self.user.height <= 0 or self.user.height > 8:
            issues.append("Invalid Height")

        if self.user.weight <= 0 or self.user.weight > 300:
            issues.append("Invalid Weight")

        return issues

    def generate_safety_report(self):

        issues = self.run_safety_checks()

        print("\n========== AI SAFETY REPORT ==========")

        if not issues:
            print("System Status : SAFE")
            print("Validation    : PASSED")
            return

        print("System Status : WARNING")
        print("Validation    : FAILED")

        print("\nDetected Issues:")

        for issue in issues:
            print(f"- {issue}")