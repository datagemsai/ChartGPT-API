# TODO Investigate LLM semantic caching techniques

# from gptcache import cache
# from gptcache.adapter import openai
# from gptcache.embedding import Onnx
# from gptcache.processor.pre import all_content
# from gptcache.manager import CacheBase, VectorBase, get_data_manager
# from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation
# from gptcache.processor.context.summarization_context import SummarizationContextProcess

# print("Cache loading.....")

# onnx = Onnx()
# data_manager = get_data_manager(CacheBase("sqlite"), VectorBase("faiss", dimension=onnx.dimension))
# context_process = SummarizationContextProcess()
# cache.init(
#     pre_embedding_func=context_process.pre_process,
#     embedding_func=onnx.to_embeddings,
#     data_manager=data_manager,
#     similarity_evaluation=SearchDistanceEvaluation(),
# )
# cache.set_openai_key()

# cache.init(pre_embedding_func=get_prompt)
# cache.set_openai_key()
