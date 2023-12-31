import random

from locust import HttpLocust, TaskSet, between, task


class GetLinkedTasks(TaskSet):
    wait_time = between(1, 5)
    questions = [
        "What is the theory of relativity?",
        "How does photosynthesis work?",
        "Explain the principles of sustainable development.",
        "How does photosynthesis work?",
        "Who wrote 'Pride and Prejudice'?",
        "Explain the process of evaporation.",
        "What causes earthquakes?",
        "Who was the first person to walk on the moon?",
        "How do airplanes stay in the air?",
        "Describe the water cycle.",
        "What is quantum mechanics?",
        "Who painted the Mona Lisa?",
        "How does the human immune system work?",
        "What is artificial intelligence?",
        "What are the Seven Wonders of the World?",
        "How do black holes form?",
        "What is the significance of the Magna Carta?",
        "Explain Newton's laws of motion.",
        "Who discovered penicillin?",
        "What causes the seasons to change?",
        "What is blockchain technology?",
        "Who was Leonardo da Vinci?",
        "How does a car engine work?",
        "What is the tallest mountain in the world?",
        "Explain the process of DNA replication.",
        "What is machine learning?",
        "How was the internet created?",
        "What causes tsunamis?",
        "Who wrote 'Romeo and Juliet'?",
        "What is the greenhouse effect?",
        "How does the stock market work?",
        "Who was Albert Einstein?",
    ]

    @task
    def post_generate(self):
        question = random.choice(self.questions)
        payload = {"inputs": question, "parameters": {"max_new_tokens": 20}}
        headers = {"Content-Type": "application/json"}
        self.client.post("/generate", json=payload, headers=headers)

    @task
    def post_generate_stream(self):
        question = random.choice(self.questions)
        payload = {"inputs": question, "parameters": {"max_new_tokens": 20}}
        headers = {"Content-Type": "application/json"}
        self.client.post("/generate_stream", json=payload, headers=headers)


class GetLinkedLocust(HttpLocust):
    task_set = GetLinkedTasks
