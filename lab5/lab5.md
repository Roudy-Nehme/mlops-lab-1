quest 1:

Loading the real model makes the test depend on MLflow and slows it down. The server could be offline or the model files missing even when the code is correct.

quest 2:

It checks that the API processes an image and returns Bread with 0.90 confidence in valid JSON. It does not check the real model's accuracy or the MLflow connection.

quest 3:

The split leakage check catches it by comparing file hashes. Duplicates can make accuracy look better because the model has already seen the test image. A corrupted image causes an obvious error.

I removed 43 existing cross-split duplicates, then all five checks passed. Copying a training image into evaluation failed the leakage check. After removing that copy, all checks passed again.

quest 4:

Run it locally after preprocessing, before training. Also run it in the training pipeline after pulling the data from DVC.

quest 5:

If a test fails, smoke is skipped. Without needs, both jobs could run at the same time, so smoke could pass even when the tests fail.

quest 6:

The [first run](https://github.com/Roudy-Nehme/mlops-lab-1/actions/runs/42843445696) took 6m 30s, and the [second](https://github.com/Roudy-Nehme/mlops-lab-1/actions/runs/42844638276) took 2m. uv sync dropped from 5s to 4s after restoring its package cache. The biggest improvement was the image build and push, from 4m 14s to 7s, after Docker reused cached layers.

quest 7:

The commit SHA identifies the code used to build the image. With latest, one machine could use an old cached image while another pulls the new one, giving them different code under the same tag.

quest 8:

The job only needs permission to read code and publish packages. Giving it more access would let a compromised step do more damage, such as pushing malicious code or changing releases.

quest 9:

In [PR #1](https://github.com/Roudy-Nehme/mlops-lab-1/pull/1), test failed and smoke was skipped. GitHub blocked the merge because main requires both checks. After I fixed the assertion, both checks passed. Everyone on the team has to pass the same checks before merging.

quest 10:

The cleaned test split has 1,055 images. Champion version 1 scored 81.23%. The margin, 2 * sqrt(p * (1 - p) / 1055), is 2.40 percentage points, so promotion needs at least 83.64%.

Version 2 (lr = 0.000001) scored 13.84% and became challenger. Version 3 (lr = 0.0001) scored 82.56% and also became challenger. Both trained for five epochs with batch size 32. Version 1 stayed champion.

I used --metric clean_test_accuracy to compare all three models on the same cleaned test data. The decisions and accuracies were saved as tags on each candidate version.

quest 11:

Run promotion automatically after training on a self-hosted runner that can reach MLflow. Another option is a hosted MLflow server, such as DagsHub, with a workflow triggered after training.

quest 12:

```text
Human: commit and push (code version = commit SHA)
  -> Auto: lint and unit tests
  -> Auto: build image and check /health with SKIP_MODEL=1
  -> Auto, main only: publish image to GHCR with the SHA tag
  -> Human: pull the image and start the container
  -> Auto at startup: load models:/food11@champion

Human: validate data, train and register a candidate
  -> Human: run promote.py --version <candidate>
  -> Auto: compare accuracies and set champion or challenger
  -> Human: restart the API to load the selected champion
```

The image's commit SHA selects the code version. The champion alias selects the model when the API starts. Deployment and starting promotion still need a human.
