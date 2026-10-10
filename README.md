# AniCare AI 🐾

**AI-powered animal disease detection and care assistance**

AniCare AI is a project focused on helping users explore animal-health information through AI-assisted disease detection. The project currently includes a cattle disease detection workflow, with work underway to expand support for dog skin diseases.

> **Important:** AniCare AI is a support tool, not a veterinary diagnosis. Predictions can be wrong. Always consult a qualified veterinarian, especially when an animal is unwell or symptoms are severe.

## ✨ Project Goals

- Analyze animal images for supported disease categories.
- Provide an accessible interface for submitting images and viewing predictions.
- Keep cattle and dog disease models separate to avoid mixing species-specific labels.
- Expand coverage carefully using correctly labeled, appropriately licensed datasets.
- Improve reliability through held-out testing and per-class evaluation.

## 🧩 Current Scope

- **Cattle disease detection:** Existing project functionality for supported cattle-disease classes.
- **Dog skin-disease detection:** Planned/in-progress extension. Dataset availability and model performance must be verified before treating this feature as ready.
- **Web interface and API:** The repository includes frontend and backend components; exact setup requirements are documented in the project files.

## 🛠️ Technology

The project report describes a Python backend using FastAPI/Uvicorn, a frontend using React and Vite, MongoDB integration, and a machine-learning image classifier. Check the actual dependency files and configuration for the current requirements.

## 📁 Project Structure

The repository is organized into frontend and backend components. The backend includes application routes/services, AI model and manifest files, scripts, tests, uploads, and dataset-related folders. Folder names may evolve as the project develops.

## 🚀 Run Locally (Windows)

1. Install **Git**, **Python**, **Node.js (LTS)**, and **MongoDB** if the current project configuration requires them.
2. Open the project folder in Visual Studio Code.
3. Review `RUN_GUIDE.md` and the relevant `README.md` files for the latest project-specific instructions.
4. Configure environment variables using `.env.example` if provided. Keep your real `.env` file private.
5. Start the backend and frontend using the commands documented in `RUN_GUIDE.md` or the project scripts.

If a root-level `run.bat` exists, review it before running it. Do not assume that every service starts successfully until you see its terminal output.

## 🧪 Testing and Model Evaluation

Use the project's test and evaluation scripts described in `RUN_GUIDE.md`. Record actual results from your own run. Do not treat reported accuracy, test counts, or model status as verified unless you reproduce them.

For machine-learning evaluation, use a held-out test set and review:
- Accuracy
- Per-class precision and recall
- Macro F1-score
- Confusion matrix
- Class balance and possible data leakage

## 📚 Datasets and Model Notes

- Use only images with reliable labels and appropriate usage rights.
- Check for corrupt images, duplicates, incorrect species, and inconsistent class names before training.
- Keep training, validation, and test sets separate; where possible, split by animal or source to reduce leakage.
- Do not upload large datasets or model weights to GitHub without checking repository size limits and dataset licenses.
- Never claim that the model detects every animal disease. Some conditions require symptoms, examination, or laboratory tests rather than an image alone.

## 🔐 Security

Before publishing this repository:
- Do **not** commit `.env` files, API keys, passwords, database connection strings, private user data, or credentials.
- Exclude virtual environments, `node_modules`, caches, and local uploads using `.gitignore`.
- Review all files staged in VS Code Source Control before committing.
- Remove any secrets from Git history if they were committed accidentally; simply deleting them in a later commit is not enough.

## 🗺️ Roadmap

- [ ] Verify the current cattle model and its evaluation results.
- [ ] Validate dataset licenses and labels.
- [ ] Add a separate dog skin-disease model.
- [ ] Expand to additional animal-health categories using suitable datasets.
- [ ] Improve uncertainty handling and veterinary guidance.
- [ ] Add reproducible setup and evaluation instructions.

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome. Before contributing, please document dataset sources and licenses, preserve existing functionality, and include tests where applicable.

## ⚖️ Disclaimer

AniCare AI is intended for educational and decision-support purposes only. It does not replace professional veterinary examination, diagnosis, or treatment. Do not use predictions alone to choose medicines or delay urgent veterinary care.
