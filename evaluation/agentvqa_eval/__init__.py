__version__ = "0.2.0"


def manifests():
    from lmms_eval.models.registry_v2 import ModelManifest

    return ModelManifest(
        model_id="agentvqa_api",
        simple_class_path="agentvqa_eval.model.AgentVQAModel",
    )
