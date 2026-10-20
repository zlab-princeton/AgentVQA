window.AGENTVQA_DATA = {
  "revision": "71b71013c61e67198609f2d724f1068b77a11277",
  "examples": [
    {
      "id": "screenspot-17",
      "displayQuestion": "To complete the instruction ‘Update the application that can be upgraded to V1.8.0 after upgrading’, which of the following actions should be performed?",
      "displayGoal": "Update the application.",
      "domain": "Web Agents",
      "subset": "Screenspot",
      "row": 17,
      "title": "Grounding a specific update control",
      "question": "To complete the instruction 'update application that can be upgraded to V1.8.0 after upgrading', which of the following actions should be performed?\n\nThe point should be on the object perfectly and not even slighly off of it if the correct answer is choosing a coordinate.",
      "options": [
        "Tap: [945, 230]",
        "Tap: [946, 742]",
        "Tap: [1016, 792]",
        "Tap: [540, 2270]"
      ],
      "answer": 2,
      "goal": "update application",
      "history": "",
      "images": [
        "assets/examples/screenspot-17-0.png"
      ],
      "sizes": [
        [
          1080,
          2400
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 2
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 1
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 1
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 1
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/Screenspot/train?row=17"
    },
    {
      "id": "screenspot-pro-13",
      "displayQuestion": "To complete the instruction ‘Click Blur Dissolve’, which of the following actions should be performed?",
      "displayGoal": "Click Blur Dissolve.",
      "domain": "Web Agents",
      "subset": "Screenspot-Pro",
      "row": 13,
      "title": "Selecting a named video transition",
      "question": "To complete the instruction 'Click Blur Dissolve', which of the following actions should be performed?\n\nThe point should be on the object perfectly and not even slighly off of it if the correct answer is choosing a coordinate.",
      "options": [
        "Tap: [461, 1359]",
        "Tap: [584, 1340]",
        "Tap: [700, 1371]",
        "Tap: [490, 588]"
      ],
      "answer": 2,
      "goal": "Blur Dissolve",
      "history": "",
      "images": [
        "assets/examples/screenspot-pro-13-0.png"
      ],
      "sizes": [
        [
          3456,
          2234
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 1
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 1
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 1
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 1
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/Screenspot-Pro/train?row=13"
    },
    {
      "id": "aitw-31",
      "displayQuestion": "Based on the goal and screen, what is the precise next action to perform?",
      "displayGoal": "Search for ‘acer nitro’ on Walmart, select the first entry, and add it to the cart.",
      "domain": "Web Agents",
      "subset": "AitW",
      "row": 31,
      "title": "Choosing the next step toward an episode goal",
      "question": "Based on the goal and screen, what is the precise next action to perform?\n\nThe point should be on the object perfectly and not even slighly off of it if the correct answer is choosing a coordinate.",
      "options": [
        "Tap: [496, 1092] ",
        "Tap: [360, 1170]",
        "Swipe: Swipe Up",
        "Type: 'walmart'"
      ],
      "answer": 2,
      "goal": "Search for \"acer nitro\" on walmart, select the first entry, and add it to the cart.",
      "history": "",
      "images": [
        "assets/examples/aitw-31-0.png"
      ],
      "sizes": [
        [
          720,
          1440
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 0
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 3
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 0
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 0
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/AitW/train?row=31"
    },
    {
      "id": "monday-4",
      "displayQuestion": "Based on the screenshot and goal, what is the correct next action to perform?",
      "displayGoal": "How do I add a Dark Mode shortcut to the iPhone Control Center (NEW 2023)?",
      "domain": "Web Agents",
      "subset": "MONDAY",
      "row": 4,
      "title": "Using the goal and previous actions",
      "question": "Based on the screenshot and goal, what is the correct next action to perform?\n\nThe point should be on the object perfectly and not even slighly off of it if the correct answer is choosing a coordinate.",
      "options": [
        "PRESS_BACK",
        "SCROLL_DOWN",
        "CLICK at [255, 127]",
        "SCROLL_UP"
      ],
      "answer": 1,
      "goal": "How to Add Dark Mode Shortcut to iPhone Control Center (NEW 2023)",
      "history": "Step 0: scrolled left while on the home screen\nStep 1: clicked at Settings icon",
      "images": [
        "assets/examples/monday-4-0.png"
      ],
      "sizes": [
        [
          511,
          1075
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 3
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 3
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 3
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 3
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/MONDAY/train?row=4"
    },
    {
      "id": "vsi-bench-1",
      "domain": "Egocentric Videos",
      "subset": "VSI-Bench",
      "row": 1,
      "title": "Reconstructing a room from a moving camera",
      "question": "If I am standing in front of the keyboard nearest to the window and facing it, is the heater to the left or the right of the keyboard?",
      "options": [
        "A. right",
        "B. left"
      ],
      "answer": 1,
      "goal": "",
      "history": "",
      "images": [],
      "sizes": [],
      "video": "https://huggingface.co/datasets/AgentVQA/AgentVQA/resolve/63352b852aec9e54c93027ebeea5f623c2d014c3/media/VSI-Bench/a1949367df7a78e58b9f6035e94f2928b9ed181b7df3df2a3e733b67fd2290e7.mp4",
      "poster": "assets/examples/vsi-bench-1-poster.jpg",
      "duration": 137.83333333333334,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 0
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 0
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 0
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 0
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/VSI-Bench/train?row=1"
    },
    {
      "id": "perception-test-0",
      "displayQuestion": "Which option correctly describes the person’s action in the video?",
      "domain": "Egocentric Videos",
      "subset": "Perception-Test",
      "row": 0,
      "title": "Distinguishing an attempted action from its outcome",
      "question": "What option related to the action did by the person in the video is correct?",
      "options": [
        "The person tried to take out a teabag from the teabox, but failed to pick up the teabag.",
        "The person put the teabag next to the cup.",
        "The person tried to pour water, but failed because the water container seems empty."
      ],
      "answer": 1,
      "goal": "",
      "history": "",
      "images": [],
      "sizes": [],
      "video": "assets/examples/perception-test-0.mp4",
      "poster": "assets/examples/perception-test-0-poster.jpg",
      "duration": 35.03971167322966,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 0
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 0
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 0
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 2
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/Perception-Test/train?row=0"
    },
    {
      "id": "openeqa-6",
      "displayQuestion": "What is the grey object below the TV in the living room?",
      "domain": "Egocentric Videos",
      "subset": "OpenEQA",
      "row": 6,
      "title": "Remembering a small object in a walkthrough",
      "question": "what is the the grey object below the TV in the living room",
      "options": [
        "a box",
        "a shelf",
        "a laptop",
        "a soundbar"
      ],
      "answer": 0,
      "goal": "",
      "history": "",
      "images": [],
      "sizes": [],
      "video": "assets/examples/openeqa-6.mp4",
      "poster": "assets/examples/openeqa-6-poster.jpg",
      "duration": 12.0,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 3
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 1
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 1
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 0
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/OpenEQA/train?row=6"
    },
    {
      "id": "videgothink-18",
      "domain": "Egocentric Videos",
      "subset": "VidEgoThink",
      "row": 18,
      "title": "Recognizing which utensil was actually used",
      "question": "Does the person use a spoon in the video?",
      "options": [
        "No.",
        "Yes",
        "Yes, for cleaning",
        "Yes, for cooking"
      ],
      "answer": 0,
      "goal": "",
      "history": "",
      "images": [],
      "sizes": [],
      "video": "https://huggingface.co/datasets/AgentVQA/AgentVQA/resolve/63352b852aec9e54c93027ebeea5f623c2d014c3/media/VidEgoThink/1c56bc576ec0e965fb8f565013f750e2d812344b4c381aca2ed13dfbb95806e0.mp4",
      "poster": "assets/examples/videgothink-18-poster.jpg",
      "duration": 198.5,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 3
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 3
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 3
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 3
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/VidEgoThink/train?row=18"
    },
    {
      "id": "egoplan-bench-17",
      "displayGoal": "Add salt to the food.",
      "domain": "Egocentric Videos",
      "subset": "EgoPlan-Bench",
      "row": 17,
      "title": "Deciding what to do next from the current observation",
      "question": "Considering the progress shown in the video and my current observation in the last frame, what action should I take next in order to add salt to the food?",
      "options": [
        "place container on window",
        "close container",
        "sprinkle salt on food",
        "pick up salt"
      ],
      "answer": 2,
      "goal": "Add salt to the food",
      "history": "",
      "images": [],
      "sizes": [],
      "video": "https://huggingface.co/datasets/AgentVQA/AgentVQA/resolve/63352b852aec9e54c93027ebeea5f623c2d014c3/media/EgoPlan-Bench/a7987638a8203ccabc516010db7b964ad7ac83614b1fe443b76d9a8f64a92448.mp4",
      "poster": "assets/examples/egoplan-bench-17-poster.jpg",
      "duration": 553.5,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 3
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 3
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 3
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 3
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/EgoPlan-Bench/train?row=17"
    },
    {
      "id": "gameqa-29",
      "displayQuestion": "Rules:\n1. The player can only walk on top of cubes.\n2. The player can climb ladders if they can reach the cube under the ladder.\n3. From a ladder, the player can reach the top of the last cube with the ladder.\n4. The blue cube is the start position; the red cube is the goal position.\n5. Numbered cubes are branch points.\n\nWhich numbered blocks are passed through when following the most direct path from start to goal?",
      "domain": "Games",
      "subset": "GameQA",
      "row": 29,
      "title": "Planning a route through a three-dimensional puzzle",
      "question": "Rules: 1. Player can only walk on top of cubes 2. Player can climb ladders if they can reach the cube under the ladder 3. From a ladder, player can reach the top of the last cube with the ladder 4. Blue cube is start position, red cube is goal position 5. Numbered cubes are branch points Which numbered blocks are passed through when following the most direct path from start to goal?",
      "options": [
        "1",
        "1, 2",
        "1, 3",
        "None",
        "3",
        "2, 3",
        "2",
        "1, 2, 3"
      ],
      "answer": 4,
      "goal": "",
      "history": "",
      "images": [
        "assets/examples/gameqa-29-0.png"
      ],
      "sizes": [
        [
          540,
          540
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 2
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 0
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 6
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 2
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/GameQA/train?row=29"
    },
    {
      "id": "marioqa-37",
      "displayQuestion": "How many coins did Mario eat before a plant appeared?",
      "domain": "Games",
      "subset": "MarioQA",
      "row": 37,
      "title": "Counting events before a visual landmark",
      "question": "How many coins did Mario eat before appearance of a plant?",
      "options": [
        "2",
        "3",
        "1",
        "4"
      ],
      "answer": 0,
      "goal": "",
      "history": "",
      "images": [],
      "sizes": [],
      "video": "assets/examples/marioqa-37-browser-main.mp4",
      "poster": "assets/examples/marioqa-37-poster.jpg",
      "duration": 5.866666666666666,
      "browser_encoded": true,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 3
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 3
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 3
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 1
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/MarioQA/train?row=37"
    },
    {
      "id": "atari-30",
      "displayQuestion": "GAME: Berzerk\n\nGAME_DESCRIPTION: You are stuck in a maze with evil robots. You must destroy them and avoid touching the walls of the maze, as this will kill you. You may be awarded extra lives after scoring a sufficient number of points, depending on the game mode. You may also be chased by an undefeatable enemy, Evil Otto, that you must avoid. Evil Otto does not appear in the default mode.\n\nGAME_VISUALS: Blue rectangular room walls forming confined spaces. Multiple small white stick figure humanoid sprites as robot enemies. One darker/yellow stick figure sprite as player character. Small white dots on floor as bullets or debris. Simple stick-figure art style with clear distinction between player and enemies. Rooms have doorway openings.\n\nREWARD_STRUCTURE: You score points for destroying robots.\n\nTASK: Action Recognition\n\nQUESTION: Which action was taken to transition from the first state to the second?\n\nChoices:\n0. UPFIRE\n1. FIRE\n2. UPRIGHTFIRE\n3. RIGHTFIRE",
      "domain": "Games",
      "subset": "Atari",
      "row": 30,
      "title": "Inferring an action between two game states",
      "question": "GAME: berzerk\n\nGAME_DESCRIPTION: You are stuck in a maze with evil robots. You must destroy them and avoid touching the walls of the maze, as this will kill you. You may be awarded extra lives after scoring a sufficient number of points, depending on the game mode. You may also be chased by an undefeatable enemy, Evil Otto, that you must avoid. Evil Otto does not appear in the default mode.\n\nGAME_VISUALS: Blue rectangular room walls forming confined spaces. Multiple small white stick figure humanoid sprites as robot enemies. One darker/yellow stick figure sprite as player character. Small white dots on floor as bullets or debris. Simple stick-figure art style with clear distinction between player and enemies. Rooms have doorway openings.\n\nREWARD_STRUCTURE: You score points for destroying robots.\n\nTASK: Action Recognition\n\nQUESTION: Which action was taken to transition from the first state to the second?\n\n**Choices:**\n0. UPFIRE\n1. FIRE\n2. UPRIGHTFIRE\n3. RIGHTFIRE\n",
      "options": [
        "UPFIRE",
        "FIRE",
        "UPRIGHTFIRE",
        "RIGHTFIRE"
      ],
      "answer": 1,
      "goal": "",
      "history": "",
      "images": [
        "assets/examples/atari-30-0.png"
      ],
      "sizes": [
        [
          1490,
          884
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 3
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 3
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 3
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 3
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/Atari/train?row=30"
    },
    {
      "id": "videogamebunny-7",
      "domain": "Games",
      "subset": "VideoGameBunny",
      "row": 7,
      "title": "Explaining the lighting in a game scene",
      "question": "What is the primary source of light illuminating the scene?",
      "options": [
        "The light from the moon",
        "A streetlight positioned above the characters.",
        "The headlights of a car approaching from the distance.",
        "The setting sun reflecting off the building in the background."
      ],
      "answer": 3,
      "goal": "",
      "history": "",
      "images": [
        "assets/examples/videogamebunny-7-0.png"
      ],
      "sizes": [
        [
          1280,
          720
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 1
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 1
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 1
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 3
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/VideoGameBunny/train?row=7"
    },
    {
      "id": "spatial-mm-4",
      "displayQuestion": "Which color is the ball in front of the girl in the green patterned jacket standing near the goalpost?",
      "domain": "Spatial Planning",
      "subset": "Spatial-MM",
      "row": 4,
      "title": "Grounding a relation among similar objects",
      "question": "which color is the ball in front of the girl in the green patterned jacket standing near the goalpost?",
      "options": [
        "yellow and white",
        "yellow and green",
        "white and black",
        "red"
      ],
      "answer": 1,
      "goal": "",
      "history": "",
      "images": [
        "assets/examples/spatial-mm-4-0.png"
      ],
      "sizes": [
        [
          2265,
          1500
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 0
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 2
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 0
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 0
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/Spatial-MM/train?row=4"
    },
    {
      "id": "omnispatial-26",
      "domain": "Spatial Planning",
      "subset": "OmniSpatial",
      "row": 26,
      "title": "Taking the diver’s perspective",
      "question": "From the diver's perspective, which side is the fish on?",
      "options": [
        "left",
        "None of the above",
        "right",
        "can not determine"
      ],
      "answer": 0,
      "goal": "",
      "history": "",
      "images": [
        "assets/examples/omnispatial-26-0.png"
      ],
      "sizes": [
        [
          1280,
          640
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 2
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 2
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 2
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 2
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/OmniSpatial/train?row=26"
    },
    {
      "id": "embspatial-bench-2",
      "displayQuestion": "Which object, in relation to your current position, holds the nearest placement in the image? Consider the closest point of the object to determine the distance.",
      "domain": "Spatial Planning",
      "subset": "EmbSpatial-Bench",
      "row": 2,
      "title": "Comparing the closest parts of objects",
      "question": "Which object, in relation to your current position, holds the nearest placement in the image? Consider closest point of the object to determine the distance.",
      "options": [
        "bread",
        "countertop",
        "garbagecan",
        "chair"
      ],
      "answer": 1,
      "goal": "",
      "history": "",
      "images": [
        "assets/examples/embspatial-bench-2-0.png"
      ],
      "sizes": [
        [
          300,
          300
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 2
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 2
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 2
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 2
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/EmbSpatial-Bench/train?row=2"
    },
    {
      "id": "space-10-2",
      "displayQuestion": "When viewing from the entrance, which description is correct?",
      "domain": "Spatial Planning",
      "subset": "SpaCE-10",
      "row": 2,
      "title": "Integrating views into a room layout",
      "question": "When viewing from the entrance, which descriptions is correct?",
      "options": [
        "A whiteboard mounted on a side wall with a plant next to it is on the left.",
        "A circular light wooden meeting table surrounded by chairs with green seats and black backrests is located in the center.",
        "A white bookshelf divided into compartments and containing books and materials, placed in the backleft corner is on the left.",
        "A curved desk with a light wooden surface positioned near large glass windows with horizontal blinds is on the left."
      ],
      "answer": 1,
      "goal": "",
      "history": "",
      "images": [
        "assets/examples/space-10-2-0.jpg",
        "assets/examples/space-10-2-1.jpg",
        "assets/examples/space-10-2-2.jpg",
        "assets/examples/space-10-2-3.jpg",
        "assets/examples/space-10-2-4.jpg",
        "assets/examples/space-10-2-5.jpg",
        "assets/examples/space-10-2-6.jpg",
        "assets/examples/space-10-2-7.jpg"
      ],
      "sizes": [
        [
          1752,
          1168
        ],
        [
          1752,
          1168
        ],
        [
          1752,
          1168
        ],
        [
          1752,
          1168
        ],
        [
          1752,
          1168
        ],
        [
          1752,
          1168
        ],
        [
          1752,
          1168
        ],
        [
          1752,
          1168
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 2
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 3
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 2
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 2
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/SpaCE-10/train?row=2"
    },
    {
      "id": "3dsrbench-36",
      "displayQuestion": "Consider the real-world 3D locations and orientations of the objects. In which direction is the bus driver trying to take the bus?",
      "domain": "Spatial Planning",
      "subset": "3DSRBench",
      "row": 36,
      "title": "Reading motion from three-dimensional orientation",
      "question": "Consider the real-world 3D locations and orientations of the objects. Which direction is the bus driver trying to take the bus to?",
      "options": [
        "right",
        "None of the above",
        "cannot say",
        "left"
      ],
      "answer": 3,
      "goal": "",
      "history": "",
      "images": [
        "assets/examples/3dsrbench-36-0.png"
      ],
      "sizes": [
        [
          1533,
          1026
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 0
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 0
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 0
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 0
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/3DSRBench/train?row=36"
    },
    {
      "id": "robo2vlm-5",
      "displayQuestion": "The robot’s task is to move the blue plastic water bottle near the green can. Which configuration shows the goal state that the robot should achieve?",
      "domain": "Robotics",
      "subset": "Robo2VLM",
      "row": 5,
      "title": "Recognizing the goal configuration",
      "question": "The robot's task is to move blue plastic water bottle near green can. Which configuration shows the goal state that the robot should achieve?",
      "options": [
        "Configuration E",
        "Configuration D",
        "Configuration B",
        "Configuration A",
        "Configuration C"
      ],
      "answer": 3,
      "goal": "",
      "history": "",
      "images": [
        "assets/examples/robo2vlm-5-0.jpg"
      ],
      "sizes": [
        [
          640,
          341
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 4
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 0
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 1
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 2
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/Robo2VLM/train?row=5"
    },
    {
      "id": "manipbench-0",
      "displayQuestion": "The robot’s task is to move the pan to the upper left of the spoon. Based on the image and task description, which of the following four choices gives the correct picking point and trajectory to complete the task?",
      "domain": "Robotics",
      "subset": "ManipBench",
      "row": 0,
      "title": "Grounding a grasp and a feasible endpoint",
      "question": "The robot task is Move the pan to the upper left of the spoon\n. Now based on the image provided and the task description, please choose the correct choice from the following 4 choices that has the correct picking point and the trajectory to get the task finished:\n\nFor trajectory choices, interpret each trajectory as starting_point, ending_point. Check that the starting point is realistically grounded on the object or handle that must be grasped, not somewhere the object is absent. Also check that the ending point is physically plausible for the task: the object should be placed, moved, opened, closed, or otherwise manipulated at the correct real-world target location without impossible or unstable placement.",
      "options": [
        "Picking point: p_8, Trajectory of the gripper: d_1,c_1",
        "Picking point: p_8, Trajectory of the gripper: d_1,b_1",
        "Picking point: p_12, Trajectory of the gripper: b_3,a_4",
        "Picking point: p_5, Trajectory of the gripper: b_4,c_0"
      ],
      "answer": 0,
      "goal": "",
      "history": "",
      "images": [
        "assets/examples/manipbench-0-0.png"
      ],
      "sizes": [
        [
          640,
          480
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 1
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 1
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 1
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 1
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/ManipBench/train?row=0"
    },
    {
      "id": "roborefit-23",
      "displayQuestion": "Will you please fetch me the brown teddy bear in a shirt on the right?",
      "displayGoal": "Will you please fetch me the brown teddy bear in a shirt on the right?",
      "domain": "Robotics",
      "subset": "Roborefit",
      "row": 23,
      "title": "Finding the intended grasp target",
      "question": "will you please fetch me the brown teddy bear in shirt on the right\n\nThe point should be on the object perfectly and not even slighly off of it if the correct answer is choosing a coordinate.",
      "options": [
        "[303, 210]",
        "[473, 376]",
        "[375, 328]",
        "[486, 298]"
      ],
      "answer": 2,
      "goal": "will you please fetch me the brown teddy bear in shirt on the right",
      "history": "",
      "images": [
        "assets/examples/roborefit-23-0.png"
      ],
      "sizes": [
        [
          640,
          480
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 1
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 1
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 1
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 1
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/Roborefit/train?row=23"
    },
    {
      "id": "share-robot-2",
      "domain": "Robotics",
      "subset": "Share-Robot",
      "row": 2,
      "title": "Tracking progress through a manipulation sequence",
      "question": "Given your progress so far (1-<pick up the broccoli>, 2-<move broccoli towards the pot>), what's the next step toward achieving <placing broccoli into a pot>?",
      "options": [
        "<drop the broccoli next to the pot>",
        "<stir the contents of the pot>",
        "<drop the broccoli into the pot>",
        "<bring brocolli above the pot>"
      ],
      "answer": 2,
      "goal": "",
      "history": "",
      "images": [
        "assets/examples/share-robot-2-0.png",
        "assets/examples/share-robot-2-1.png",
        "assets/examples/share-robot-2-2.png",
        "assets/examples/share-robot-2-3.png",
        "assets/examples/share-robot-2-4.png",
        "assets/examples/share-robot-2-5.png",
        "assets/examples/share-robot-2-6.png",
        "assets/examples/share-robot-2-7.png",
        "assets/examples/share-robot-2-8.png",
        "assets/examples/share-robot-2-9.png",
        "assets/examples/share-robot-2-10.png",
        "assets/examples/share-robot-2-11.png",
        "assets/examples/share-robot-2-12.png",
        "assets/examples/share-robot-2-13.png",
        "assets/examples/share-robot-2-14.png"
      ],
      "sizes": [
        [
          640,
          480
        ],
        [
          640,
          480
        ],
        [
          640,
          480
        ],
        [
          640,
          480
        ],
        [
          640,
          480
        ],
        [
          640,
          480
        ],
        [
          640,
          480
        ],
        [
          640,
          480
        ],
        [
          640,
          480
        ],
        [
          640,
          480
        ],
        [
          640,
          480
        ],
        [
          640,
          480
        ],
        [
          640,
          480
        ],
        [
          640,
          480
        ],
        [
          640,
          480
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 3
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 3
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 3
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 3
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/Share-Robot/train?row=2"
    },
    {
      "id": "erqa-19",
      "displayQuestion": "The purple line in the second image corresponds to which colored line in the first image?",
      "domain": "Robotics",
      "subset": "ERQA",
      "row": 19,
      "title": "Matching a direction across viewpoints",
      "question": "The purple line in the second image corresponds to which colored line in the first image? ",
      "options": [
        "Green.",
        "Yellow.",
        "Red.",
        "Blue."
      ],
      "answer": 0,
      "goal": "",
      "history": "",
      "images": [
        "assets/examples/erqa-19-0.png",
        "assets/examples/erqa-19-1.png"
      ],
      "sizes": [
        [
          320,
          180
        ],
        [
          320,
          180
        ]
      ],
      "video": null,
      "poster": null,
      "duration": null,
      "browser_encoded": false,
      "predictions": [
        {
          "family": "openai",
          "model": "gpt-5.6-luna-high",
          "answer": 1
        },
        {
          "family": "claude",
          "model": "claude-opus-4-8",
          "answer": 2
        },
        {
          "family": "gemini",
          "model": "gemini-3.1-pro",
          "answer": 2
        },
        {
          "family": "qwen",
          "model": "Qwen3.7-Flash",
          "answer": 1
        }
      ],
      "source": "https://huggingface.co/datasets/AgentVQA/AgentVQA/viewer/ERQA/train?row=19"
    }
  ],
  "results": [
    {
      "model": "GPT-5.6-sol (thinking-high)",
      "scores": [
        47.0,
        69.0,
        62.5,
        51.0,
        45.5,
        55.0
      ]
    },
    {
      "model": "GPT-5.6-sol (thinking-none)",
      "scores": [
        16.0,
        59.0,
        44.5,
        41.0,
        30.5,
        38.2
      ]
    },
    {
      "model": "GPT-5.6-luna (thinking-high)",
      "scores": [
        34.5,
        65.0,
        61.0,
        43.5,
        35.5,
        47.9
      ]
    },
    {
      "model": "GPT-5.6-luna (thinking-none)",
      "scores": [
        19.5,
        46.0,
        37.5,
        32.0,
        29.0,
        32.8
      ]
    },
    {
      "model": "GPT-4o",
      "scores": [
        21.5,
        40.0,
        29.0,
        35.0,
        31.5,
        31.4
      ]
    },
    {
      "model": "Gemini 3.1 Pro",
      "scores": [
        34.5,
        64.0,
        68.0,
        61.0,
        51.0,
        55.7
      ]
    },
    {
      "model": "Gemini 3.7 Flash",
      "scores": [
        40.5,
        67.0,
        70.0,
        62.5,
        52.5,
        58.5
      ]
    },
    {
      "model": "Claude Opus 4.8",
      "scores": [
        35.5,
        60.0,
        50.5,
        41.0,
        33.0,
        44.0
      ]
    },
    {
      "model": "Claude Sonnet 5",
      "scores": [
        38.0,
        47.0,
        53.0,
        42.5,
        36.5,
        43.4
      ]
    },
    {
      "model": "GLM-4.6V",
      "scores": [
        25.5,
        54.0,
        47.5,
        39.5,
        42.5,
        41.8
      ]
    },
    {
      "model": "GLM-4.5V",
      "scores": [
        25.0,
        65.0,
        46.5,
        41.0,
        37.0,
        42.9
      ]
    },
    {
      "model": "GLM-4.1V-9B-Thinking",
      "scores": [
        19.0,
        53.0,
        41.0,
        38.5,
        25.5,
        35.4
      ]
    },
    {
      "model": "GLM-4.1V-9B-Base",
      "scores": [
        20.5,
        46.0,
        37.5,
        44.5,
        33.0,
        36.3
      ]
    },
    {
      "model": "Kimi K3",
      "scores": [
        22.0,
        64.0,
        63.5,
        53.0,
        39.0,
        48.3
      ]
    },
    {
      "model": "Llama 4 Maverick",
      "scores": [
        18.5,
        49.0,
        23.0,
        30.0,
        19.5,
        28.0
      ]
    },
    {
      "model": "Qwen3.8 27B",
      "scores": [
        30.0,
        69.0,
        61.5,
        51.5,
        42.5,
        50.9
      ]
    },
    {
      "model": "Qwen3.7 Plus",
      "scores": [
        32.5,
        60.0,
        61.5,
        50.0,
        39.0,
        48.6
      ]
    },
    {
      "model": "Qwen3.7 Flash",
      "scores": [
        43.0,
        72.5,
        61.0,
        55.0,
        43.5,
        55.0
      ]
    },
    {
      "model": "Qwen3.5 397B-A17B",
      "scores": [
        25.0,
        65.0,
        57.5,
        51.5,
        40.0,
        47.8
      ]
    },
    {
      "model": "Qwen3.5 122B-A10B",
      "scores": [
        26.0,
        60.0,
        53.0,
        50.0,
        41.0,
        46.0
      ]
    },
    {
      "model": "Qwen3.5 35B-A3B",
      "scores": [
        34.5,
        62.0,
        55.5,
        45.5,
        42.0,
        47.9
      ]
    },
    {
      "model": "Qwen3.5 27B",
      "scores": [
        32.5,
        57.0,
        49.5,
        51.5,
        43.0,
        46.7
      ]
    }
  ],
  "models": {
    "openai": "GPT-5.6-luna · High",
    "claude": "Claude Opus 4.8",
    "gemini": "Gemini 3.1 Pro",
    "qwen": "Qwen3.7-Flash"
  },
  "domains": [
    {
      "name": "Web Agents",
      "color": "#ff0102",
      "ink": "#a71420",
      "tint": "#fff0f1"
    },
    {
      "name": "Egocentric Videos",
      "color": "#1aac13",
      "ink": "#207318",
      "tint": "#eff9ed"
    },
    {
      "name": "Games",
      "color": "#016cff",
      "ink": "#145cc1",
      "tint": "#edf4ff"
    },
    {
      "name": "Spatial Planning",
      "color": "#8f3edc",
      "ink": "#7230ad",
      "tint": "#f5edfc"
    },
    {
      "name": "Robotics",
      "color": "#fe6300",
      "ink": "#a24408",
      "tint": "#fff3e8"
    }
  ]
};
