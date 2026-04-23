from services import agent_evaluation_service, agent_observability_service


DEFAULT_DATASET_NAME = "newscopilot-planner-baseline"


def get_runtime_status() -> dict:
    return {
        "langsmithReady": agent_observability_service.LANGSMITH_SDK_INSTALLED,
        "langsmithConfigured": agent_observability_service.is_langsmith_configured(),
        "datasetUploadReady": agent_observability_service.is_langsmith_configured(),
        "project": agent_observability_service.settings.langsmith_project,
        "defaultDatasetName": DEFAULT_DATASET_NAME,
    }


def build_export_payload(*, limit: int = 20, case_ids: list[str] | None = None, dataset_name: str | None = None) -> dict:
    cases = agent_evaluation_service.load_eval_dataset()
    if case_ids:
        wanted = set(case_ids)
        cases = [case for case in cases if case.case_id in wanted]
    cases = cases[:limit]

    examples = []
    for case in cases:
        examples.append(
            {
                "inputs": {
                    "question": case.question,
                    "mode": case.mode,
                    "timeRange": case.time_range,
                    "category": case.category,
                },
                "outputs": {
                    "expectedPlan": case.expected_plan,
                    "expectedIntent": case.expected_intent,
                    "expectedFreshness": case.expected_freshness,
                    "expectedScope": case.expected_scope,
                },
                "metadata": {
                    "caseId": case.case_id,
                    "title": case.title,
                },
            }
        )

    return {
        "datasetName": dataset_name or DEFAULT_DATASET_NAME,
        "exampleCount": len(examples),
        "examples": examples,
    }


def sync_dataset(*, limit: int = 20, case_ids: list[str] | None = None, dataset_name: str | None = None) -> dict:
    if not agent_observability_service.is_langsmith_configured():
        return {
            "synced": False,
            "datasetName": dataset_name or DEFAULT_DATASET_NAME,
            "exampleCount": 0,
            "datasetId": None,
            "note": "LangSmith 未配置，当前仅支持本地导出。",
        }

    payload = build_export_payload(limit=limit, case_ids=case_ids or [], dataset_name=dataset_name)
    client = agent_observability_service.LANGSMITH_CLIENT
    dataset = client.create_dataset(
        dataset_name=payload["datasetName"],
        description="NewsCopilot planner and query-analysis baseline dataset",
    )
    client.create_examples(
        dataset_id=dataset.id,
        inputs=[item["inputs"] for item in payload["examples"]],
        outputs=[item["outputs"] for item in payload["examples"]],
        metadata=[item["metadata"] for item in payload["examples"]],
    )
    return {
        "synced": True,
        "datasetName": payload["datasetName"],
        "exampleCount": payload["exampleCount"],
        "datasetId": str(dataset.id),
        "note": "LangSmith 数据集已创建，可在平台继续做评测与实验。",
    }

