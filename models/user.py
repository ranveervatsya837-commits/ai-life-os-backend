class User:

    def __init__(self, name, age, mood, sleep, water, exercise, health_score, height, weight):
        self.name = name
        self.age = age
        self.mood = mood
        self.sleep = sleep
        self.water = water
        self.exercise = exercise
        self.health_score = health_score
        self.height = height
        self.weight = weight

    def show_profile(self):
        print("\n--- User Profile ---")
        print("Name:", self.name)
        print("Age:", self.age)
        print("Height:", self.height)
        print("Weight:", self.weight)
        print("Mood:", self.mood)
        print("Sleep:", self.sleep)
        print("Water:", self.water)
        print("Exercise:", self.exercise)
        print("Health Score:", self.health_score)

    def calculate_health_score(self):
        score = 0

        if self.mood == "good":
            score += 1

        if self.sleep >= 7:
            score += 1

        if self.water == "yes":
            score += 1

        if self.exercise == "yes":
            score += 1

        self.health_score = score

        return score