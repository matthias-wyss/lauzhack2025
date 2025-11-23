// src/App.jsx

"use client";
import Image from "next/image";
import React, { useState, useEffect, useRef } from "react";

const PIPELINE_STEPS = ["Extract", "Enrich", "Design", "Code"];

export default function App() {
  const [selectedTab, setSelectedTab] = useState("overview");
  const [pipelineStep, setPipelineStep] = useState("idle");

  const [whiteboardImage, setWhiteboardImage] = useState(null);
  const [audioName, setAudioName] = useState(null);

  const [overview, setOverview] = useState(
    "No project generated yet. Upload a whiteboard image and audio, then run the pipeline."
  );
  const [architecture, setArchitecture] = useState("");
  const [code, setCode] = useState("");

  // New backend fields
  const [zipBase64, setZipBase64] = useState("");
  const [projectRoot, setProjectRoot] = useState("");
  const [structureJson, setStructureJson] = useState("");

  // Webcam overlay visibility
  const [showWebcam, setShowWebcam] = useState(false);

  const [audioUrl, setAudioUrl] = useState(null);
  const [showAudioRecorder, setShowAudioRecorder] = useState(false);

  const [whiteboardFile, setWhiteboardFile] = useState(null); // File | null
  const [audioFile, setAudioFile] = useState(null); // File or Blob | null

  const handleWhiteboardUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const url = URL.createObjectURL(file);
    setWhiteboardImage(url);
    setWhiteboardFile(file);
  };

  const handleAudioUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setAudioName(file.name);
    const url = URL.createObjectURL(file);
    setAudioUrl(url);
    setAudioFile(file);
  };

  const clearWhiteboardImage = () => {
    setWhiteboardImage(null);
    setWhiteboardFile(null);
  };

  const clearAudio = () => {
    setAudioName(null);
    setAudioUrl(null);
    setAudioFile(null);
  };

  const handleGenerate = async () => {
    if (!whiteboardFile && !audioFile) {
      alert("Add a whiteboard image or an audio file first.");
      return;
    }

    const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

    // Animate the first steps (all except the last one)
    const animatePipeline = async () => {
      for (let i = 0; i < PIPELINE_STEPS.length - 1; i++) {
        setPipelineStep(PIPELINE_STEPS[i]);
        await sleep(100);
      }
    };

    const animationPromise = animatePipeline();

    try {
      const formData = new FormData();
      if (whiteboardFile) {
        formData.append("image", whiteboardFile);
      }
      if (audioFile) {
        formData.append("audio", audioFile, audioName || "audio.webm");
      }

      const res = await fetch("http://localhost:8000/process", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        console.error("Backend error", res.status);
        alert("Backend error while processing.");
        setPipelineStep("idle");
        return;
      }

      const data = await res.json();

      // Update UI from backend response
      setOverview(data.overview || "");
      setArchitecture(data.architecture || "");
      setCode(data.code || "");

      // New fields from backend
      setZipBase64(data.zip_base64 || "");
      setProjectRoot(data.project_root || "");
      setStructureJson(data.structure_json || "");

      await animationPromise;

      const lastStep = PIPELINE_STEPS[PIPELINE_STEPS.length - 1]; // "Code"
      setPipelineStep(lastStep);
      await sleep(400);
      setPipelineStep("done");
    } catch (err) {
      console.error("Network error:", err);
      alert("Could not reach backend.");
      setPipelineStep("idle");
    }
  };

  const isRunning =
    pipelineStep !== "idle" && pipelineStep !== "done" && pipelineStep !== "";

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 flex flex-col">
      <Header />

      <main className="flex-1 flex flex-col px-4 md:px-8 py-4 gap-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 flex-1">
          <InputPanel
            onWhiteboardUpload={handleWhiteboardUpload}
            onAudioUpload={handleAudioUpload}
            onOpenWebcam={() => setShowWebcam(true)}
            onAudioRecord={() => setShowAudioRecorder(true)}
          />

          <PreviewPanel
            whiteboardImage={whiteboardImage}
            audioName={audioName}
            audioUrl={audioUrl}
            pipelineStep={pipelineStep}
            isRunning={isRunning}
            onGenerate={handleGenerate}
            onClearWhiteboardImage={clearWhiteboardImage}
            onClearAudio={clearAudio}
          />

          <OutputPanel
            selectedTab={selectedTab}
            setSelectedTab={setSelectedTab}
            overview={overview}
            architecture={architecture}
            code={code}
            zipBase64={zipBase64}
            projectRoot={projectRoot}
          />
        </div>
      </main>

      {/* Webcam and audio recorder overlays */}
      <WebcamOverlay
        isOpen={showWebcam}
        onClose={() => setShowWebcam(false)}
        onCapture={async (dataUrl) => {
          setWhiteboardImage(dataUrl);

          const res = await fetch(dataUrl);
          const blob = await res.blob();
          const file = new File([blob], "webcam_capture.png", { type: blob.type });
          setWhiteboardFile(file);

          setShowWebcam(false);
        }}
      />

      <AudioRecorderOverlay
        isOpen={showAudioRecorder}
        onClose={() => setShowAudioRecorder(false)}
        onSave={(blob, url) => {
          setAudioName("Recorded audio");
          setAudioUrl(url);
          setAudioFile(blob);
          setShowAudioRecorder(false);
        }}
      />
    </div>
  );
}

function Header() {
  return (
    <header className="border-b border-slate-800 px-4 md:px-8 py-3 flex items-center justify-between bg-slate-950/80 backdrop-blur">
      <div className="flex items-center gap-3">
        <div className="h-9 w-9 rounded-xl overflow-hidden shadow-lg shadow-cyan-500/30 flex items-center justify-center bg-slate-900 border border-slate-800">
          <Image
            src="/specter.jpg"
            alt="Specter Logo"
            width={40}
            height={40}
            className="object-cover"
          />
        </div>
        <div>
          <h1 className="text-sm md:text-base font-semibold">Specter Project</h1>
          <p className="text-xs text-slate-400">Turn your ideas into reality</p>
        </div>
      </div>
      <div className="flex items-center gap-3 text-xs">
        <span className="badge badge-outline border-slate-700 text-slate-300">
          Powered by AI
        </span>
      </div>
    </header>
  );
}

function InputPanel({
  onWhiteboardUpload,
  onAudioUpload,
  onOpenWebcam,
  onAudioRecord,
}) {
  return (
    <section className="card bg-slate-900/70 border border-slate-800 shadow-xl rounded-2xl">
      <div className="card-body p-4 space-y-5">
        <h2 className="card-title text-sm mb-1">Inputs</h2>

        {/* Whiteboard */}
        <div className="space-y-2">
          <h3 className="text-[11px] font-semibold uppercase tracking-wide text-slate-300">
            Whiteboard
          </h3>
          <p className="text-xs text-slate-400">
            Upload a snapshot of your brainstorming whiteboard or capture it
            directly from the camera.
          </p>

          <label className="border border-dashed border-slate-700 rounded-xl flex flex-col items-center justify-center gap-1 py-4 text-xs cursor-pointer hover:border-cyan-400 hover:bg-slate-900/70 transition">
            <span className="text-sm font-medium">Upload whiteboard image</span>
            <span className="text-slate-500">PNG / JPG / JPEG</span>
            <input
              type="file"
              accept="image/*"
              className="hidden"
              onChange={onWhiteboardUpload}
            />
          </label>

          <button
            className="btn btn-sm btn-outline w-full rounded-xl border-slate-700 hover:border-cyan-400"
            onClick={onOpenWebcam}
          >
            Capture from webcam
          </button>
        </div>

        {/* Audio */}
        <div className="space-y-2">
          <h3 className="text-[11px] font-semibold uppercase tracking-wide text-slate-300">
            Audio
          </h3>
          <p className="text-xs text-slate-400">
            Upload or record the brainstorming discussion to capture context.
          </p>

          <label className="border border-dashed border-slate-700 rounded-xl flex flex-col items-center justify-center gap-1 py-4 text-xs cursor-pointer hover:border-cyan-400 hover:bg-slate-900/70 transition">
            <span className="text-sm font-medium">Upload audio</span>
            <span className="text-slate-500">MP3 / WAV / M4A</span>
            <input
              type="file"
              accept="audio/*"
              className="hidden"
              onChange={onAudioUpload}
            />
          </label>

          <button
            className="btn btn-sm btn-outline w-full rounded-xl border-slate-700 hover:border-cyan-400"
            onClick={onAudioRecord}
          >
            Record audio
          </button>
        </div>
      </div>
    </section>
  );
}

function PreviewPanel({
  whiteboardImage,
  audioName,
  audioUrl,
  pipelineStep,
  isRunning,
  onGenerate,
  onClearWhiteboardImage,
  onClearAudio,
}) {
  return (
    <section className="card bg-slate-900/70 border border-slate-800 shadow-xl rounded-2xl">
      <div className="card-body p-4 space-y-4">
        <h2 className="card-title text-sm mb-1">Preview & Pipeline</h2>

        {/* Whiteboard preview */}
        <div className="relative rounded-2xl border border-slate-800 bg-slate-950/70 min-h-[180px] flex items-center justify-center overflow-hidden">
          {whiteboardImage ? (
            <>
              <Image
                src={whiteboardImage}
                alt="Whiteboard preview"
                fill
                sizes="(min-width: 1024px) 33vw, 100vw"
                className="object-contain"
              />
              <button
                onClick={onClearWhiteboardImage}
                className="absolute top-2 right-2 bg-black/50 hover:bg-gray-700 text-white text-xs px-2 py-1 rounded-lg"
              >
                ✕
              </button>
            </>
          ) : (
            <span className="text-xs text-slate-500">
              Whiteboard preview will appear here
            </span>
          )}
        </div>

        {/* Audio chip */}
        <div className="text-xs border border-slate-800 bg-slate-950/80 rounded-xl px-3 py-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="inline-flex h-5 w-5 items-center justify-center rounded-full bg-cyan-500/20 text-cyan-300 text-[11px]">
                ♪
              </span>
              <span className="text-slate-300 flex items-center gap-2">
                Audio:{" "}
                <span className="text-slate-400">
                  {audioName ? (
                    <>
                      {audioName}
                      <button
                        onClick={onClearAudio}
                        className="ml-1 bg-black/50 hover:bg-gray-700 text-white text-[10px] px-1 py-0.5 rounded-lg"
                      >
                        ✕
                      </button>
                    </>
                  ) : (
                    "No audio uploaded"
                  )}
                </span>
              </span>
            </div>
          </div>
          {audioUrl && (
            <audio src={audioUrl} controls className="mt-2 w-full" />
          )}
        </div>

        {/* Pipeline */}
        <PipelineTimeline step={pipelineStep} />

        {/* Generate button */}
        <button
          className={`btn w-full rounded-xl mt-1 border-0 ${
            isRunning
              ? "bg-slate-700 text-slate-300 cursor-not-allowed"
              : "bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-500/20"
          }`}
          onClick={onGenerate}
          disabled={isRunning}
        >
          {isRunning
            ? "Running multi-agent pipeline..."
            : "Generate project from inputs"}
        </button>
      </div>
    </section>
  );
}

function PipelineTimeline({ step }) {
  const currentIndex =
    step === "idle" || step === "done"
      ? -1
      : PIPELINE_STEPS.findIndex((s) => s === step);

  return (
    <div className="text-xs">
      <p className="text-slate-400 mb-2">Multi-agent pipeline</p>
      <div className="flex flex-wrap items-center gap-2">
        {PIPELINE_STEPS.map((s, idx) => {
          const isActive = idx === currentIndex;
          const isCompleted = idx < currentIndex || step === "done";

          return (
            <React.Fragment key={s}>
              <div
                className={[
                  "px-3 py-1 rounded-full border text-[11px] uppercase tracking-wide",
                  isActive &&
                    "border-cyan-400 bg-cyan-500/20 text-cyan-100 shadow shadow-cyan-500/30",
                  isCompleted &&
                    "border-emerald-500 bg-emerald-500/15 text-emerald-100",
                  !isActive &&
                    !isCompleted &&
                    "border-slate-700 text-slate-400",
                ]
                  .filter(Boolean)
                  .join(" ")}
              >
                {s}
              </div>
              {idx < PIPELINE_STEPS.length - 1 && (
                <div className="w-4 h-px bg-slate-700 hidden md:block" />
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}

function OutputPanel({
  selectedTab,
  setSelectedTab,
  overview,
  architecture,
  code,
  zipBase64,
  projectRoot,
}) {
  const tabs = [
    { id: "overview", label: "Overview" },
    { id: "architecture", label: "Architecture" },
    { id: "code", label: "Code" },
  ];

  const content = {
    overview,
    architecture,
    code,
  }[selectedTab];

  const handleDownloadZip = () => {
    if (!zipBase64) {
      alert("No project archive available yet. Run the pipeline first.");
      return;
    }

    try {
      const byteChars = atob(zipBase64);
      const byteNumbers = new Array(byteChars.length);
      for (let i = 0; i < byteChars.length; i++) {
        byteNumbers[i] = byteChars.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: "application/zip" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${projectRoot || "project"}.zip`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Failed to download ZIP:", e);
      alert("Could not download ZIP file.");
    }
  };

  return (
    <section className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 flex flex-col">
      <h2 className="text-sm font-semibold mb-2">Outputs</h2>

      {/* Tabs */}
      <div className="flex gap-2 mb-3 text-xs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setSelectedTab(tab.id)}
            className={`px-3 py-1.5 rounded-full border transition ${
              selectedTab === tab.id
                ? "border-cyan-400 bg-cyan-500/15 text-cyan-100"
                : "border-slate-700 text-slate-300 hover:bg-slate-800"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex-1 rounded-xl border border-slate-800 bg-slate-950/60 p-3 overflow-auto text-xs whitespace-pre-wrap text-slate-100">
        {content || "Run the pipeline to view generated outputs here."}
      </div>

      {/* Export actions */}
      <div className="mt-3 flex justify-between items-center text-[11px]">
        <span className="text-slate-500">
          Tip: copy text into your IDE or GitHub repo.
        </span>
        <div className="flex gap-2">
          <button
            className="px-3 py-1 rounded-full border border-slate-700 hover:bg-slate-800"
            onClick={() => navigator.clipboard.writeText(content || "")}
          >
            Copy current tab
          </button>
          <button
            className={`px-3 py-1 rounded-full border border-slate-700 hover:bg-slate-800 ${
              !zipBase64 ? "opacity-50 cursor-not-allowed" : ""
            }`}
            onClick={handleDownloadZip}
            disabled={!zipBase64}
          >
            Download ZIP
          </button>
        </div>
      </div>
    </section>
  );
}

/* ---------- Webcam and audio recorder overlays ---------- */

function AudioRecorderOverlay({ isOpen, onClose, onSave }) {
  const [isRecording, setIsRecording] = useState(false);
  const [localAudioUrl, setLocalAudioUrl] = useState(null);

  const [audioDevices, setAudioDevices] = useState([]);
  const [selectedMicId, setSelectedMicId] = useState("");

  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const streamRef = useRef(null);

  const onCloseInternal = () => {
    if (isRecording) {
      stopRecording();
    }
    onClose();
    setSelectedMicId("");
  };

  // Enumerate mics when overlay opens
  useEffect(() => {
    if (!isOpen) return;

    let cancelled = false;

    (async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        if (cancelled) return;

        const mics = devices.filter((d) => d.kind === "audioinput");
        setAudioDevices(mics);

        const defaultId = mics[0]?.deviceId || "";
        setSelectedMicId((prev) => prev || defaultId);

        if (!defaultId) {
          alert("No microphone devices found.");
        }
      } catch (err) {
        console.error("Error enumerating audio devices:", err);
        alert("Could not list microphone devices.");
        onCloseInternal();
      }
    })();

    return () => {
      cancelled = true;
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }
      if (localAudioUrl) {
        URL.revokeObjectURL(localAudioUrl);
      }
    };
  }, [isOpen]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleMicChange = (e) => {
    setSelectedMicId(e.target.value);
  };

  const startRecording = async () => {
    try {
      if (!selectedMicId) {
        alert("Please select a microphone first.");
        return;
      }

      // Clean old stream if any
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((t) => t.stop());
        streamRef.current = null;
      }

      const constraints = {
        audio: { deviceId: { exact: selectedMicId } },
      };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;

      chunksRef.current = [];
      const recorder = new MediaRecorder(stream);
      mediaRecorderRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        const url = URL.createObjectURL(blob);
        setLocalAudioUrl((prev) => {
          if (prev) URL.revokeObjectURL(prev);
          return url;
        });
        onSave(blob, url); // send to parent
      };

      recorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone:", err);
      alert("Could not access this microphone.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const handleClose = () => {
    if (isRecording) {
      stopRecording();
    }
    onCloseInternal();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl p-4 w-full max-w-md flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold">Record brainstorming audio</h3>
          <button
            className="btn btn-xs btn-ghost text-slate-400 hover:text-slate-100"
            onClick={handleClose}
          >
            ✕
          </button>
        </div>

        {/* Microphone selection */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400">Microphone:</span>
          <select
            className="select select-xs w-full max-w-xs bg-slate-900 border-slate-700 text-xs"
            value={selectedMicId}
            onChange={handleMicChange}
          >
            {audioDevices.length === 0 && (
              <option value="">No microphones found</option>
            )}
            {audioDevices.map((dev) => (
              <option
                key={dev.deviceId}
                value={dev.deviceId}
                className="hover:bg-slate-800"
              >
                {dev.label || `Microphone ${dev.deviceId.slice(0, 8)}`}
              </option>
            ))}
          </select>
        </div>

        <div className="text-xs text-slate-300">
          <p>
            Press <span className="font-semibold">Start</span> to record your
            discussion, then <span className="font-semibold">Stop</span> to
            attach it to this session.
          </p>
        </div>

        <div className="flex items-center justify-center gap-3 mt-2">
          <button
            className={`btn btn-sm rounded-full ${
              isRecording
                ? "btn-disabled bg-slate-700 text-slate-300"
                : "bg-emerald-500 hover:bg-emerald-400 border-0 text-slate-950"
            }`}
            onClick={startRecording}
            disabled={isRecording}
          >
            ⏺ Start
          </button>
          <button
            className={`btn btn-sm rounded-full ${
              isRecording
                ? "bg-red-500 hover:bg-red-400 border-0 text-white"
                : "btn-disabled bg-slate-700 text-slate-300"
            }`}
            onClick={stopRecording}
            disabled={!isRecording}
          >
            ⏹ Stop & Save
          </button>
        </div>

        {localAudioUrl && (
          <div className="mt-2">
            <p className="text-xs text-slate-400 mb-1">Last recording:</p>
            <audio src={localAudioUrl} controls className="w-full" />
          </div>
        )}
      </div>
    </div>
  );
}

function WebcamOverlay({ isOpen, onClose, onCapture }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);

  const [videoDevices, setVideoDevices] = useState([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState("");

  const stopStream = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
  };

  const onCloseInternal = () => {
    stopStream();
    onClose();
    setSelectedDeviceId("");
  };

  const startStream = async (deviceId) => {
    try {
      stopStream();
      const constraints = {
        video: deviceId ? { deviceId: { exact: deviceId } } : true,
      };
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (err) {
      console.error("Error accessing webcam:", err);
      alert("Could not access this camera.");
    }
  };

  useEffect(() => {
    if (!isOpen) return;

    let cancelled = false;

    (async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        if (cancelled) return;

        const videos = devices.filter((d) => d.kind === "videoinput");
        setVideoDevices(videos);

        const defaultId = videos[0]?.deviceId || "";
        setSelectedDeviceId((prev) => prev || defaultId);

        if (defaultId) {
          await startStream(defaultId);
        } else {
          alert("No camera devices found.");
        }
      } catch (err) {
        console.error("Error enumerating devices:", err);
        alert("Could not list camera devices.");
        onCloseInternal();
      }
    })();

    return () => {
      cancelled = true;
      stopStream();
    };
  }, [isOpen]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleDeviceChange = async (e) => {
    const newId = e.target.value;
    setSelectedDeviceId(newId);
    if (newId) {
      await startStream(newId);
    }
  };

  const handleCaptureClick = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    const width = video.videoWidth || 640;
    const height = video.videoHeight || 480;
    canvas.width = width;
    canvas.height = height;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, width, height);

    const dataUrl = canvas.toDataURL("image/png");
    onCapture(dataUrl);
    setSelectedDeviceId("");
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl p-4 w-full max-w-2xl flex flex-col gap-4">
        <div className="flex items-center justify-between mb-1">
          <h3 className="text-sm font-semibold">Capture whiteboard from webcam</h3>
          <button
            className="btn btn-xs btn-ghost text-slate-400 hover:text-slate-100"
            onClick={onCloseInternal}
          >
            ✕
          </button>
        </div>

        {/* Camera selection */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-slate-400">Camera:</span>
          <select
            className="select select-xs w-full max-w-xs bg-slate-900 border-slate-700 text-xs"
            value={selectedDeviceId}
            onChange={handleDeviceChange}
          >
            {videoDevices.length === 0 && (
              <option value="">No cameras found</option>
            )}
            {videoDevices.map((dev) => (
              <option
                key={dev.deviceId}
                value={dev.deviceId}
                className="hover:bg-slate-800"
              >
                {dev.label || `Camera ${dev.deviceId.slice(0, 8)}`}
              </option>
            ))}
          </select>
        </div>

        <div className="relative rounded-xl overflow-hidden border border-slate-800 bg-black aspect-video">
          <video
            ref={videoRef}
            className="w-full h-full object-contain"
            autoPlay
            playsInline
            muted
          />
        </div>

        {/* Hidden canvas used just for snapshot */}
        <canvas ref={canvasRef} className="hidden" />

        <div className="flex justify-end gap-2 text-xs">
          <button
            className="btn btn-sm btn-ghost rounded-full"
            onClick={onCloseInternal}
          >
            Cancel
          </button>
          <button
            className="btn btn-sm rounded-full bg-cyan-500 hover:bg-cyan-400 border-0 text-slate-950"
            onClick={handleCaptureClick}
          >
            Capture
          </button>
        </div>
      </div>
    </div>
  );
}
