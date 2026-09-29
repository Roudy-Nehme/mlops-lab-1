quest 1:

Without a volume, the MLflow data is stored only inside that container. If I remove the container and start a new one, the database and artifacts are gone and the MLflow UI starts empty

quest 2:

A named volume is managed by Docker and keeps MLflow data separate from the containers. A bind mount would also work, but it depends on a specific folder on the host machine.

quest 3:

Docker Compose puts the services on the same private network, so containers can reach each other by service name. That is why 'mlflow' resolves to the MLflow container.

quest 4:

The frontend reads INFERENCE_URL from an environment variable so the same image can run in different environments. Outside Compose, it can use another URL such as localhost without changing the code.

quest 5:

The inference service does not need a host port because only the frontend needs to contact it. Inside Docker Compose, the frontend can reach it directly at `http://inference:8000`.

quest 6:

'depends_on' only starts MLflow first; it does not guarantee MLflow is ready. If inference tries to load the model too early, it can fail and the inference container may exit.

quest 7:

'docker compose ps' shows the three services running. MLflow publishes port 5000 and the frontend publishes port 8501, while the inference service has no host port.

quest 8:

After moving the 'champion' alias to version 2, I restarted the inference service with 'docker compose restart inference' so it would load the new promoted model.

quest 9:

The restart works because the model is loaded when the inference application starts. Restarting the container starts the application again, so it loads the model currently pointed to by 'champion'.
docker compose down

quest 10:

After docker compose down and docker compose up, the registered model and champion alias were still there because the MLflow data is stored in a named volume. Using docker compose down -v would delete the volume, so the MLflow data would be lost.

quest 11:

Docker Compose is designed for a single machine. For multiple replicas, load balancing, and surviving machine failures, I would use an orchestrator such as Kubernetes and store MLflow data in external persistent storage.