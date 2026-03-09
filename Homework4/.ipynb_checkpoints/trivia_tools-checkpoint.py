import html
import requests


class TriviaTools:
    def get_categories(self) -> str:
        url = "https://opentdb.com/api_category.php"
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        categories = data.get("trivia_categories")
        if not categories:
            return f"Could not load categories. Full response: {data}"

        return "\n".join(f"{cat['id']}: {cat['name']}" for cat in categories)

    def get_questions(self, amount: int, category: int, difficulty: str) -> str:
        """Fetch trivia questions.
    
        Args:
            amount: Number of questions (1-10)
            category: Category ID
            difficulty: easy, medium, or hard
        """
        params = {
            "amount": amount,
            "category": category,
            "difficulty": difficulty,
            "type": "multiple",
        }
    
        url = "https://opentdb.com/api.php"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        response_code = data.get("response_code")
        if response_code != 0:
            return f"Trivia API error. response_code={response_code}. Full response: {data}"

        results = data.get("results")
        if not results:
            return f"No questions returned. Full response: {data}"

        lines = []
        for i, q in enumerate(results, 1):
            question = html.unescape(q["question"])
            correct = html.unescape(q["correct_answer"])
            wrong = [html.unescape(a) for a in q["incorrect_answers"]]
            lines.append(f"Question {i}: {question}")
            lines.append(f"  Correct answer: {correct}")
            lines.append(f"  Wrong answers: {', '.join(wrong)}")
            lines.append("")

        return "\n".join(lines)