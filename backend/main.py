from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from agent import create_code

import os
import io
import json
import zipfile
import base64

app = FastAPI()

# Allow your Next.js dev server to talk to the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production: put your domain instead of "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def zip_directory_to_bytes(dir_path: str) -> bytes:
  """
  Walk a directory and return a ZIP archive as bytes.
  """
  buf = io.BytesIO()
  with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
      for root, dirs, files in os.walk(dir_path):
          for filename in files:
              full_path = os.path.join(root, filename)
              rel_path = os.path.relpath(full_path, dir_path)
              zf.write(full_path, arcname=rel_path)
  buf.seek(0)
  return buf.getvalue()


def build_code_tree(root_dir: str) -> str:
  """
  Produce a simple textual tree of the project:
  MyApp/
    frontend/
      index.html
    backend/
      main.py
  """
  lines = []
  root_name = os.path.basename(os.path.abspath(root_dir))
  lines.append(f"{root_name}/")

  for current_root, dirs, files in os.walk(root_dir):
      rel = os.path.relpath(current_root, root_dir)
      if rel == ".":
          indent_level = 0
      else:
          indent_level = rel.count(os.sep) + 1

      if rel != ".":
          indent = "  " * indent_level
          lines.append(f"{indent}{os.path.basename(current_root)}/")

      sub_indent = "  " * (indent_level + 1)
      for f in files:
          lines.append(f"{sub_indent}{f}")

  return "\n".join(lines)


def analyze_structure_json(structure_json_str: str, project_root: str) -> str:
  """
  Human-readable analysis of the project organization based on the JSON
  the creator agent returned.
  """
  try:
      data = json.loads(structure_json_str)
  except Exception as e:
      return f"Could not parse project structure JSON: {e}"

  lines = [f"Project root: {project_root}", "", "Folders:"]

  for folder_name, folder_content in data.items():
      if not isinstance(folder_content, dict):
          continue

      # Count files in this logical folder
      file_paths = [
          k for k, v in folder_content.items()
          if k != "functions" and isinstance(v, str)
      ]
      lines.append(f"- {folder_name}: {len(file_paths)} files")

  # Rough language / file-type stats
  ext_counts: dict[str, int] = {}
  for folder_content in data.values():
      if not isinstance(folder_content, dict):
          continue
      for path, desc in folder_content.items():
          if path == "functions" or not isinstance(desc, str):
              continue
          _, ext = os.path.splitext(path)
          if ext:
              ext_counts[ext] = ext_counts.get(ext, 0) + 1

  if ext_counts:
      lines.append("")
      lines.append("Languages / file types:")
      for ext, count in ext_counts.items():
          lines.append(f"- {ext}: {count} files")

  return "\n".join(lines)


@app.post("/process")
async def process_project(
    image: UploadFile | None = File(None),
    audio: UploadFile | None = File(None),
):
    """
    image: whiteboard photo (from upload or webcam)
    audio: brainstorming audio (uploaded or recorded)
    """

    overview = ""
    structure_json_str = ""
    project_root = ""
    
    have_audio = audio is not None
    have_image = image is not None

    if image is not None:
        image_bytes = await image.read()

        # Save image to disk (for your OCR/model)
        with open("input_image.jpg", "wb") as f:
            f.write(image_bytes)

    if audio is not None:
        audio_bytes = await audio.read()
        
        with open("input_audio.wav", "wb") as f:
            f.write(audio_bytes)
        
            
    # Run your agent pipeline: returns spec, structure JSON, and project root folder
    spec, structure_json_str, project_root, competition_output = create_code(
        image_path="input_image.jpg" if have_image else None,
        audio_url="input_audio.wav" if have_audio else None,
    )

    # If for some reason project_root is empty (e.g., no image), avoid crashes
    if not project_root:
        project_root = "GeneratedProject"  # or None; up to you

    # Build textual code tree (to show in your "Code" tab)
    if os.path.exists(project_root):
        code_tree = build_code_tree(project_root)
        # Zip the folder
        zip_bytes = zip_directory_to_bytes(project_root)
        zip_base64 = base64.b64encode(zip_bytes).decode("utf-8")
    else:
        code_tree = "Project folder not found on server."
        zip_base64 = ""

    # Analyze the project structure into a human-readable summary
    if structure_json_str:
        architecture_analysis = analyze_structure_json(structure_json_str, project_root)
    else:
        architecture_analysis = "No project structure JSON available."


    return {
        "overview": spec,
        "architecture": architecture_analysis,
        "code": code_tree,
        "zip_base64": zip_base64,
        "project_root": project_root,
        "structure_json": structure_json_str,
        "competition_analysis": competition_output,
    }
