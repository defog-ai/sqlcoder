# Defog SQLCoder
Defog's SQLCoder is a state-of-the-art LLM for converting natural language questions to SQL queries.

[Interactive Demo](https://defog.ai/sqlcoder-demo/) | [🤗 HF Repo](https://huggingface.co/defog/sqlcoder) | [♾️ Colab](https://colab.research.google.com/drive/1z4rmOEiFkxkMiecAWeTUlPl0OmKgfEu7?usp=sharing) | [🐦 Twitter](https://twitter.com/defogdata)

## TL;DR
SQLCoder is a 15B parameter model that outperforms `gpt-3.5-turbo` for natural language to SQL generation tasks on our [sql-eval](https://github.com/defog-ai/sql-eval) framework, and significantly outperforms all popular open-source models. It also significantly outperforms `text-davinci-003`, a model that's more than 10 times its size.

SQLCoder is fine-tuned on a base StarCoder model.

## Results
| model   | perc_correct |
|-|-|  
| gpt-4            | 74.3 |
| defog-sqlcoder   | 64.6 |
| gpt-3.5-turbo    | 60.6 |
| defog-easysql    | 57.1 |   
| text-davinci-003 | 54.3 |
| wizardcoder      | 52.0 |
| starcoder        | 45.1 |

## Training
Defog was trained on 10,537 human-curated questions across 2 epochs. These questions were based on 10 different schemas. None of the schemas in the training data were included in our evaluation framework.

Training happened in 2 phases. The first phase was on questions that were classified as "easy" or "medium" difficulty, and the second phase was on questions that were classified as "hard" or "extra hard" difficulty.

The results of training on our easy+medium data were stored in a model called `defog-easy`. We found that the additional training on hard+extra-hard data led to a 7 percentage point increase in performance.

## Results by question category
We classified each generated question into one of 5 categories. The table displays the percentage of questions answered correctly by each model, broken down by category.
| query_category | gpt-4 | defog-sqlcoder | gpt-3.5-turbo | defog-easy | text-davinci-003 | wizard-coder | star-coder |
|-|-|-|-|-|-|-|-|  
| group_by | 82.9 | 77.1 | 71.4 | 62.9 | 62.9 | 68.6 | 54.3 |
| order_by | 71.4 | 65.7 | 60.0 | 68.6 | 60.0 | 54.3 | 57.1 |
| ratio | 62.9 | 57.1 | 48.6 | 40.0 | 37.1 | 22.9 | 17.1 |
| table_join | 74.3 | 57.1 | 60.0 | 54.3 | 51.4 | 54.3 | 51.4 |
| where | 80.0 | 65.7 | 62.9 | 60.0 | 60.0 | 60.0 | 45.7 |

## Using SQLCoder
You can use SQLCoder via the `transformers` library by downloading our model weights from the HuggingFace repo. We have added sample code for [inference](./inference.py) on a [sample database schema](./metadata.sql). 
```bash
python inference.py -q "Question about the sample database goes here"

# Sample questions:
```

You can also use a demo on our website [here](https://defog.ai/sqlcoder-demo), or run SQLCoder in Colab [here](https://colab.research.google.com/drive/13BIKsqHnPOBcQ-ba2p77L5saiepTIwu0#scrollTo=ZpbVgVHMkJvC)

## Hardware Requirements
SQLCoder has been tested on an A100 40GB GPU with `bfloat16` weights. You can also load an 8-bit and 4-bit quantized version of the model on consumer GPUs with 20GB or more of memory – like RTX 4090, RTX 3090, and Apple M2 Pro, M2 Max, or M2 Ultra Chips with 20GB or more of memory.

## Todo

- [x] Open-source the v1 model weights
- [ ] Train the model on more data, with higher data variance
- [ ] Tune the model further with Reward Modelling and RLHF
- [ ] Pretrain a model from scratch that specializes in SQL analysis
