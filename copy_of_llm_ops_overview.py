# -*- coding: utf-8 -*-
"""Copy of llm_ops_overview.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1J1C0AofjO-eI1DQzVKaFZAaeP4Dc6iGd

<center>
    <p style="text-align:center">
        <img alt="phoenix logo" src="https://storage.googleapis.com/arize-phoenix-assets/assets/phoenix-logo-light.svg" width="200"/>
        <br>
        <a href="https://docs.arize.com/phoenix/">Docs</a>
        |
        <a href="https://github.com/Arize-ai/phoenix">GitHub</a>
        |
        <a href="https://join.slack.com/t/arize-ai/shared_invite/zt-1px8dcmlf-fmThhDFD_V_48oU7ALan4Q">Community</a>
    </p>
</center>
<h1 align="center">LLM Ops - Tracing, Evaluation, and Analysis</h1>

In this tutorial we will learn how to build, observe, evaluate, and analyze a LLM powered application.

It has the following sections:

1. Understanding LLM-powered applications
2. Observing the application using traces
3. Evaluating the application using LLM Evals
4. Exploring and and troubleshooting the application using UMAP projection and clustering

⚠️ This tutorial requires an OpenAI key to run


## Understanding LLM powered applications

Building software with LLMs, or any machine learning model, is [fundamentally different](https://karpathy.medium.com/software-2-0-a64152b37c35). Rather than compiling source code into binary to run a series of commands, we need to navigate datasets, embeddings, prompts, and parameter weights to generate consistent accurate results. LLM outputs are probabilistic and therefore don't produce the same deterministic outcome every time.

<img src="https://raw.githubusercontent.com/Arize-ai/phoenix-assets/main/images/blog/5_steps_of_building_llm_app.png" width="1100" />

There's a lot that can go into building an LLM application, but let's focus on the architecture. Below is a diagram of one possible architecture. In this diagram we see that the application is built around an LLM but that there are many other components that are needed to make the application work.

<img src="https://raw.githubusercontent.com/Arize-ai/phoenix-assets/main/images/blog/llm_app_architecture.png" width="1100" />

The complexity that is involved in building an LLM application is why observability is so important. Observability is the ability to understand the internal state of a system by examining its inputs and outputs. Each step of the response generation process needs to be monitored, evaluated and tuned to provide the best possible experience. Not only that, certain tradeoffs might need to be made to optimize for speed, cost, or accuracy. In the context of LLM applications, we need to be able to understand the internal state of the system by examining telemetry data such as LLM Traces.

## Observing the application using traces

LLM Traces and Observability lets us understand the system from the outside, by letting us ask questions about that system without knowing its inner workings. Furthermore, it allows us to easily troubleshoot and handle novel problems (i.e. “unknown unknowns”), and helps us answer the question, “Why is this happening?”

LLM Traces are designed to be a category of telemetry data that is used to understand the execution of LLMs and the surrounding application context such as retrieval from vector stores and the usage of external tools such as search engines or APIs. It lets you understand the inner workings of the individual steps your application takes wile also giving you visibility into how your system is running and performing as a whole.

Traces are made up of a sequence of `spans`. A span represents a unit of work or operation (think a span of time). It tracks specific operations that a request makes, painting a picture of what happened during the time in which that operation was executed.

LLM Tracing supports the following span kinds:

<img src="https://raw.githubusercontent.com/Arize-ai/phoenix-assets/main/images/blog/span_kinds.png" width="1100"/>


By capturing the building blocks of your application while it's running, phoenix can provide a more complete picture of the inner workings of your application. To illustrate this, let's look at an example LLM application and inspect it's traces.

### Traces and Spans in action

Let's build a relatively simple LLM-powered application that will answer questions about Arize AI. This example uses LlamaIndex for RAG and OpenAI as the LLM but you could use any LLM you would like. The details of the application are not important, but the architecture is. Let's get started.
"""

# Commented out IPython magic to ensure Python compatibility.
# %pip install -Uqq "arize-phoenix[evals,llama-index,embeddings]" "llama-index-llms-openai" "openai>=1" gcsfs nest_asyncio 'httpx<0.28'

import os
from getpass import getpass

# if not (openai_api_key := os.getenv("OPENAI_API_KEY")):
#     openai_api_key = getpass("🔑 Enter your OpenAI API key: ")

os.environ["OPENAI_API_KEY"] = 

import phoenix as px

px.launch_app().view()

!pip install openinference-instrumentation-llama_index

from openinference.instrumentation.llama_index import LlamaIndexInstrumentor

from phoenix.otel import register

tracer_provider = register(endpoint="http://127.0.0.1:6006/v1/traces")
LlamaIndexInstrumentor().instrument(skip_dep_check=True, tracer_provider=tracer_provider)

from openinference.instrumentation.openai import OpenAIInstrumentor

from phoenix.otel import register

tracer_provider = register(endpoint="http://127.0.0.1:6006/v1/traces")

OpenAIInstrumentor().instrument(skip_dep_check=True, tracer_provider=tracer_provider)

from gcsfs import GCSFileSystem
from llama_index.core import (
    Settings,
    StorageContext,
    load_index_from_storage,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

import phoenix as px

file_system = GCSFileSystem(project="public-assets-275721")
index_path = "arize-phoenix-assets/datasets/unstructured/llm/llama-index/arize-docs/index/"
storage_context = StorageContext.from_defaults(
    fs=file_system,
    persist_dir=index_path,
)

Settings.llm = OpenAI(model="gpt-4-turbo-preview")
Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")
index = load_index_from_storage(
    storage_context,
)
query_engine = index.as_query_engine()

"""Now that we have an application setup, let's take a look inside."""

from tqdm import tqdm

queries = [
    "How can I query for a monitor's status using GraphQL?",
    "How do I delete a model?",
    "How much does an enterprise license of Arize cost?",
    "How do I log a prediction using the python SDK?",
]

for query in tqdm(queries):
    response = query_engine.query(query)
    print(f"Query: {query}")
    print(f"Response: {response}")

"""Now that we've run the application a few times, let's take a look at the traces in the UI"""

print("The Phoenix UI:", px.active_session().url)

"""The UI will give you an interactive troubleshooting experience. You can sort, filter, and search for traces. You can also view the detail of each trace to better understand what happened during the response generation process.

<img src="https://storage.googleapis.com/arize-phoenix-assets/assets/images/trace_details_view.png" width="1100"/>

In addition to being able to view the traces in the UI, you can also query for traces to use as pandas dataframes in your notebook.
"""

spans_df = px.Client().get_spans_dataframe()
spans_df[["name", "span_kind", "attributes.input.value", "attributes.retrieval.documents"]].head()

"""With just a few lines of code, we have managed to gain visibility into the inner workings of our application. We can now better understand how things like retrieval, prompts, and parameter weights could be affecting our application. But what can we do with this information? Let's take a look at how to use LLM evals to evaluate our application."""

if (
    input("The tutorial is about to move on to the evaluation section. Continue [Y/n]?")
    .lower()
    .startswith("n")
):
    assert False, "notebook stopped"

"""## Evaluating the application using LLM Evals

Evaluation should serve as the primary metric for assessing your application. It determines whether the app will produce accurate responses based on the data sources and range of queries.

While it's beneficial to examine individual queries and responses, this approach is impractical as the volume of edge-cases and failures increases. Instead, it's more effective to establish a suite of metrics and automated evaluations. These tools can provide insights into overall system performance and can identify specific areas that may require scrutiny.

Let's first convert our traces into a workable datasets
"""

from phoenix.session.evaluation import get_qa_with_reference, get_retrieved_documents

retrieved_documents_df = get_retrieved_documents(px.active_session())
queries_df = get_qa_with_reference(px.active_session())

"""We can now use Phoenix's LLM Evals to evaluate these queries. LLM Evals uses an LLM to grade your application based on different criteria. For this example we will use the evals library to see if any `hallucinations` are present and if the `Q&A Correctness` is good (whether or not the application answers the question correctly)."""

import nest_asyncio

from phoenix.evals import (
    HALLUCINATION_PROMPT_RAILS_MAP,
    HALLUCINATION_PROMPT_TEMPLATE,
    QA_PROMPT_RAILS_MAP,
    QA_PROMPT_TEMPLATE,
    OpenAIModel,
    llm_classify,
)

nest_asyncio.apply()  # Speeds up OpenAI API calls

# Check if the application has any indications of hallucinations
hallucination_eval = llm_classify(
    dataframe=queries_df,
    model=OpenAIModel(model="gpt-4o", temperature=0.0),
    template=HALLUCINATION_PROMPT_TEMPLATE,
    rails=list(HALLUCINATION_PROMPT_RAILS_MAP.values()),
    provide_explanation=True,  # Makes the LLM explain its reasoning
)
hallucination_eval["score"] = (
    hallucination_eval.label[~hallucination_eval.label.isna()] == "factual"
).astype(int)

# Check if the application is answering questions correctly
qa_correctness_eval = llm_classify(
    dataframe=queries_df,
    model=OpenAIModel(model="gpt-4o", temperature=0.0),
    template=QA_PROMPT_TEMPLATE,
    rails=list(QA_PROMPT_RAILS_MAP.values()),
    provide_explanation=True,  # Makes the LLM explain its reasoning
    concurrency=4,
)

qa_correctness_eval["score"] = (
    qa_correctness_eval.label[~qa_correctness_eval.label.isna()] == "correct"
).astype(int)

hallucination_eval.head()

qa_correctness_eval.head()

"""As you can see from the results, one of the queries was flagged as a hallucination. Let's log these results to the phoenix server to view the hallucinations in the UI."""

from phoenix.trace import SpanEvaluations

px.Client().log_evaluations(
    SpanEvaluations(eval_name="Hallucination", dataframe=hallucination_eval),
    SpanEvaluations(eval_name="QA Correctness", dataframe=qa_correctness_eval),
)

"""Now that we have the hallucinations logged, let's take a look at them in the UI. You will notice that the traces that correspond to hallucinations are clearly marked in the UI and you can now query for them!"""

print("The Phoenix UI:", px.active_session().url)

"""We've now identified that there are certain queries that are resulting in hallucinations or incorrect answers. Let's see if we can use LLM Evals to identify if these issues are caused by the retrieval process for RAG. We are going to use an LLM to grade whether or not the chunks retrieved are relevant to the query."""

from phoenix.evals import (
    RAG_RELEVANCY_PROMPT_RAILS_MAP,
    RAG_RELEVANCY_PROMPT_TEMPLATE,
    OpenAIModel,
    llm_classify,
)

retrieved_documents_eval = llm_classify(
    dataframe=retrieved_documents_df,
    model=OpenAIModel(model="gpt-4o", temperature=0.0),
    template=RAG_RELEVANCY_PROMPT_TEMPLATE,
    rails=list(RAG_RELEVANCY_PROMPT_RAILS_MAP.values()),
    provide_explanation=True,
)

retrieved_documents_eval["score"] = (
    retrieved_documents_eval.label[~retrieved_documents_eval.label.isna()] == "relevant"
).astype(int)

retrieved_documents_eval.head()

"""Looks like we are getting a lot of irrelevant chunks of text that might be polluting the prompt sent to the LLM. Let's log these evals to phoenix, at which point phoenix will automatically calculate retrieval metrics for us."""

from phoenix.trace import DocumentEvaluations

px.Client().log_evaluations(
    DocumentEvaluations(eval_name="Relevance", dataframe=retrieved_documents_eval)
)

"""If we once again visit the UI, we will now see that Phoenix has aggregated up retrieval metrics (`precision`, `ndcg`, and `hit`). We see that our hallucinations and incorrect answers directly correlate to bad retrieval!"""

print("The Phoenix UI:", px.active_session().url)

"""<img src="https://raw.githubusercontent.com/Arize-ai/phoenix-assets/main/images/screenshots/document_evals_on_traces.png" />

There are many more evaluations metrics that can be used to make determinations about the quality of your application. Phoenix supports evaluating not only traces but individual spans (such as retrievers) as well as performing retrieval analysis for your document chunks. Evaluation metrics can also be customized for your specific use-case. For more details, consult the phoenix docs.
"""

if (
    input("The tutorial is about to move on to the analysis section. Continue [Y/n]?")
    .lower()
    .startswith("n")
):
    assert False, "notebook stopped"

px.close_app()  # Close the Phoenix UI

"""## Exploring and and troubleshooting the application using UMAP projection and clustering

We have so far figured out how to trace our application and how to evaluate it. But what if we need to understand the application at a higher level? What if we need to understand if the application is performing badly for a certain topic or if there are any patterns in the data that we can use to improve the application? This is where UMAP projection and clustering comes in. UMAP and clustering let's you view the query embeddings of your application in a 3D space. This allows you to see patterns in the data and understand how your application is performing in various clusters (semantic groups).

Since we only ran the application for 4 queries, we won't be able to see any patterns in the data. Let's pull in a larger dataset of queries and run the application again.
"""

import pandas as pd

# Pull in queries from the LLM
query_df = pd.read_parquet(
    "http://storage.googleapis.com/arize-phoenix-assets/datasets/unstructured/llm/llama-index/arize-docs/query_data_complete3.parquet",
)

query_ds = px.Inferences.from_open_inference(query_df)

query_ds.dataframe.head()

"""Let's also pull in the embeddings for our knowledge base. This will allow us to see how how document chunks are being retrieved by the application."""

import numpy as np


def storage_context_to_dataframe(storage_context: StorageContext) -> pd.DataFrame:
    """Converts the storage context to a pandas dataframe.

    Args:
        storage_context (StorageContext): Storage context containing the index
        data.

    Returns:
        pd.DataFrame: The dataframe containing the index data.
    """
    document_ids = []
    document_texts = []
    document_embeddings = []
    docstore = storage_context.docstore
    vector_store = storage_context.vector_store
    for node_id, node in docstore.docs.items():
        document_ids.append(node.hash)  # use node hash as the document ID
        document_texts.append(node.text)
        document_embeddings.append(np.array(vector_store.get(node_id)))
    return pd.DataFrame(
        {
            "document_id": document_ids,
            "text": document_texts,
            "text_vector": document_embeddings,
        }
    )


database_df = storage_context_to_dataframe(storage_context)
database_df = database_df.drop_duplicates(subset=["text"])
database_df.head()

"""Let's now launch Phoenix with these two datasets."""

# get a random sample of 500 documents (including retrieved documents)
# this will be handled by by the application in a coming release
num_sampled_point = 500
retrieved_document_ids = set(
    [
        doc_id
        for doc_ids in query_df[":feature.[str].retrieved_document_ids:prompt"].to_list()
        for doc_id in doc_ids
    ]
)
retrieved_document_mask = database_df["document_id"].isin(retrieved_document_ids)
num_retrieved_documents = len(retrieved_document_ids)
num_additional_samples = num_sampled_point - num_retrieved_documents
unretrieved_document_mask = ~retrieved_document_mask
sampled_unretrieved_document_ids = set(
    database_df[unretrieved_document_mask]["document_id"]
    .sample(n=num_additional_samples, random_state=0)
    .to_list()
)
sampled_unretrieved_document_mask = database_df["document_id"].isin(
    sampled_unretrieved_document_ids
)
sampled_document_mask = retrieved_document_mask | sampled_unretrieved_document_mask
sampled_database_df = database_df[sampled_document_mask]

database_schema = px.Schema(
    prediction_id_column_name="document_id",
    prompt_column_names=px.EmbeddingColumnNames(
        vector_column_name="text_vector",
        raw_data_column_name="text",
    ),
)
database_ds = px.Inferences(
    dataframe=sampled_database_df,
    schema=database_schema,
    name="database",
)

(session := px.launch_app(primary=query_ds, corpus=database_ds, run_in_thread=False)).View()

"""Using Phoenix's embedding projection feature, we can now view the query embeddings in a 3D space. What you are looking at is a point-cloud where each point represents a query. When embeddings are projected into a lower dimensional space, UMAP preserves the semantic distance that the embeddings encode. This means that the points that are closer together are more similar. This allows us to see patterns in the data and understand how our application is performing in various clusters. If you click through the clusters, you will see clusters of queries that are significantly farther away from the knowledge base. This means that the knowledge base does not contain enough information to answer the user's question (In this case, the document chunks don't contain any information about pricing. Can you find this cluster?).

Phoenix's embedding view also supports coloring and cluster metrics by evaluations! This means you can use it to find pockets of poor user feedback or hallucinations. Phoenix's embedding view supports embeddings for text, images, and video so a most forms of unstructured data can be analyzed.

Last but not least, Phoenix can draw the connections between queries and the document chunks. This allows you to see which document chunks are being retrieved for each query and to visualize the semantic distance between them.

<img src="https://github.com/Arize-ai/phoenix-assets/raw/main/gifs/corpus_search_and_retrieval.gif?raw=true" />

## Conclusion

Phoenix is a powerful companion for building LLM-powered applications. It allows you to observe, evaluate, and explore your application at every step of you development process. For more details, consult the [phoenix docs](https://docs.arize.com/phoenix).
"""