REPOSITORY = "AgentVQA/AgentVQA"
REVISION = "71b71013c61e67198609f2d724f1068b77a11277"
LMMS_REVISION = "e14b5084660fad0f3e057a8699a57b1c028e8269"
DOMAINS = {
    "Web Agents": ("AitW", "MONDAY", "Screenspot", "Screenspot-Pro"),
    "Games": ("Atari", "GameQA", "MarioQA", "VideoGameBunny"),
    "Egocentric Videos": (
        "EgoPlan-Bench",
        "OpenEQA",
        "Perception-Test",
        "VidEgoThink",
        "VSI-Bench",
    ),
    "Robotics": ("ERQA", "ManipBench", "Robo2VLM", "Roborefit", "Share-Robot"),
    "Spatial Understanding": (
        "3DSRBench",
        "EmbSpatial-Bench",
        "OmniSpatial",
        "SpaCE-10",
        "Spatial-MM",
    ),
}
SUBSETS = {s: d for d, names in DOMAINS.items() for s in names}
COUNTS = {s: 200 // len(DOMAINS[d]) for s, d in SUBSETS.items()}
POINT_SUBSETS = {"AitW", "MONDAY", "Screenspot", "Screenspot-Pro", "ERQA", "Roborefit"}
PUBLIC_FIELDS = (
    "Question",
    "Options",
    "Episode Goal",
    "Action History",
    "Image",
    "Images",
    "Video",
)


def task_name(subset):
    return "agentvqa_" + subset.lower().replace("-", "_")


def select_subsets(subsets=None, domains=None):
    chosen = set(subsets or ())
    unknown = chosen - SUBSETS.keys()
    if unknown:
        raise ValueError(f"Unknown subsets: {sorted(unknown)}")
    for domain in domains or ():
        if domain not in DOMAINS:
            raise ValueError(f"Unknown domain: {domain}")
        chosen.update(DOMAINS[domain])
    return [s for s in SUBSETS if not chosen or s in chosen]
