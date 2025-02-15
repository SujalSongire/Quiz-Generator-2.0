from flask import Flask, render_template, request, session, redirect, url_for
import requests
import random

app = Flask(__name__, template_folder="templates")
app.secret_key = 'your_secret_key'  # Required for session management

# Dictionary mapping topics & difficulty levels to API URLs
QUESTION_URLS = {
    "general_knowledge": {
        "easy": "https://opentdb.com/api.php?amount=10&category=9&difficulty=easy&type=multiple",
        "medium": "https://opentdb.com/api.php?amount=10&category=9&difficulty=medium&type=multiple",
        "hard": "https://opentdb.com/api.php?amount=10&category=9&difficulty=hard&type=multiple"
    },
    "computer": {
        "easy": "https://opentdb.com/api.php?amount=10&category=18&difficulty=easy&type=multiple",
        "medium": "https://opentdb.com/api.php?amount=10&category=18&difficulty=medium&type=multiple",
        "hard": "https://opentdb.com/api.php?amount=10&category=18&difficulty=hard&type=multiple"
    },
    "history": {
        "easy": "https://opentdb.com/api.php?amount=10&category=23&difficulty=easy&type=multiple",
        "medium": "https://opentdb.com/api.php?amount=10&category=23&difficulty=medium&type=multiple",
        "hard": "https://opentdb.com/api.php?amount=10&category=23&difficulty=hard&type=multiple"
    },
    "mathematics": {
        "easy": "https://opentdb.com/api.php?amount=10&category=19&difficulty=easy&type=multiple",
        "medium": "https://opentdb.com/api.php?amount=10&category=19&difficulty=medium&type=multiple",
        "hard": "https://opentdb.com/api.php?amount=10&category=19&difficulty=hard&type=multiple"
    }
}

def get_questions(topic, difficulty):
    url = QUESTION_URLS.get(topic, {}).get(difficulty)

    if not url:
        print(f"Invalid topic or difficulty: {topic}, {difficulty}")
        return []

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get('results', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching questions: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_difficulty/<topic>')
def select_difficulty(topic):
    if topic not in QUESTION_URLS:
        return "Invalid topic selected."
    return render_template('select_difficulty.html', topic=topic)

@app.route('/start_quiz/<topic>/<difficulty>')
def start_quiz(topic, difficulty):
    session.clear()
    questions = get_questions(topic, difficulty)

    if not questions:
        return "Failed to fetch questions. Try again later."

    session['questions'] = questions
    session['topic'] = topic
    session['score'] = 0
    session['current_question'] = 0
    session['feedback'] = None
    session['selected_answer'] = None
    return redirect(url_for('quiz'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'questions' not in session or session['current_question'] >= len(session['questions']):
        return redirect(url_for('result'))

    question = session['questions'][session['current_question']]

    if f'choices_{session["current_question"]}' not in session:
        choices = question['incorrect_answers'] + [question['correct_answer']]
        random.shuffle(choices)
        session[f'choices_{session["current_question"]}'] = choices
    else:
        choices = session[f'choices_{session["current_question"]}']

    correct_answer = question['correct_answer']
    session['correct_answer'] = correct_answer

    feedback = session.get('feedback', None)
    selected_answer = session.get('selected_answer', None)

    if request.method == 'POST':
        user_answer = request.form.get('answer')
        session['selected_answer'] = user_answer

        if user_answer == correct_answer:
            session['score'] += 1
            session['feedback'] = "Correct! 🎉"
        else:
            session['feedback'] = f"Incorrect ❌. The correct answer was: {correct_answer}"

        return redirect(url_for('quiz'))

    return render_template(
        'quiz.html',
        question=question,
        choices=choices,
        q_num=session['current_question'] + 1,
        feedback=feedback,
        selected_answer=selected_answer,
        correct_answer=correct_answer
    )

@app.route('/next')
def next_question():
    session['current_question'] += 1
    session['feedback'] = None
    session['selected_answer'] = None
    return redirect(url_for('quiz'))

@app.route('/result')
def result():
    score = session.get('score', 0)
    total = len(session.get('questions', []))
    return render_template('result.html', score=score, total=total)

if __name__ == '__main__':
    app.run(debug=True)
