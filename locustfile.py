from locust import HttpUser, task, between


class BlogUser(HttpUser):
    wait_time = between(1, 3)  # Пауза между запросами 1-3 сек

    @task
    def get_posts(self) -> None:
        self.client.get("/posts/?limit=20")

    @task
    def get_comments(self) -> None:
        self.client.get("/posts/67f2c815983810c0365f6b7b/comments?limit=20")

    @task
    def get_answers(self) -> None:
        self.client.get(
            "/posts/67f2c815983810c0365f6b7b/comments/67f5c92df5516cb8a5b7b99c/replies?limit=20"
        )
