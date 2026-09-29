quest 1:
pyproject.toml was updated with the new dependencies such as MLflow, PyTorch, torchvision and scikit-learn. It also contains the PyTorch CPU index configuration. uv.lock was updated with the exact versions of these packages and all of their dependencies to make the environment reproducible.

quest 2:
--backend-store-uri tells MLflow where to store experiment metadata such as runs, parameters and metrics. In this lab it uses the mlflow.db SQLite database.
--default-artifact-root tells MLflow where to store files produced by runs, such as trained models. Here they are stored in the mlruns folder.
Metadata is information describing the experiment, while artifacts are actual files produced by the experiment.

quest 3: 
mlflow.db and mlruns/ should not be tracked by Git because they are generated experiment outputs and can change frequently or become large. They should not be tracked by DVC either because MLflow already manages experiment runs and artifacts, while DVC is being used for versioning the datasets.

quest 4:
The first time mlflow.set_experiment("food11") is called, MLflow checks whether the experiment exists. If it does not exist, MLflow automatically creates a new experiment named food11. It then appears in the MLflow UI.

quest 5:
mlflow.log_param is used to record parameters that are fixed before training, such as the learning rate, batch size, number of epochs, or model architecture. mlflow.log_metric records values produced during training, such as loss and accuracy. Metrics use a step because their values can change at each epoch, allowing MLflow to plot their evolution over time. Parameters do not need a step because they stay fixed for the whole run.

quest 6:
n the MLflow UI, the parameters are shown in the Params section and the losses and accuracies appear as metrics and charts. The trained model is stored as an artifact. Since the MLflow server was started with --default-artifact-root ./mlruns, the model artifact is physically stored inside the local mlruns folder in the project.
 
 quest 7:
 The learning rate 0.0001 gave the best validation accuracy, with a final val_accuracy of about 0.7673. A higher learning rate is not always better. In our experiments, 0.01 performed much worse, with a validation accuracy of only 0.1770.

 quest 8:
 The parallel coordinates plot shows that the learning rate has a strong effect on validation accuracy. The best result is with lr = 0.0001 and batch_size = 32, reaching about 0.767 validation accuracy. A much larger learning rate, 0.01, gives the worst result at about 0.177. For lr = 0.001, increasing the batch size from 32 to 64 improves validation accuracy slightly, from about 0.533 to 0.585. Overall, a smaller learning rate performed better in these experiments.
 
qeust 9:
After sorting the runs by val_accuracy in descending order, the best run is legendary-wasp-473. It used lr = 0.0001 and batch_size = 32, with a final val_accuracy of about 0.7673.
The Run ID is: 4511211e41144e88a4960ee152eabffa