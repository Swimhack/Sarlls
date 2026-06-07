import { useCallback, useEffect, useRef, useState } from 'react';
import { RotateCcw, ZoomIn, ZoomOut, Maximize2, Box } from 'lucide-react';

const MODEL_VIEWER_SRC =
  'https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js';

function useModelViewerReady() {
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (customElements.get('model-viewer')) {
      setLoaded(true);
      return;
    }
    const script = document.createElement('script');
    script.type = 'module';
    script.src = MODEL_VIEWER_SRC;
    script.onload = () => {
      // model-viewer registers asynchronously after the module loads
      const check = () => {
        if (customElements.get('model-viewer')) setLoaded(true);
        else setTimeout(check, 100);
      };
      check();
    };
    document.head.appendChild(script);
  }, []);

  return loaded;
}

const BOARD_SPECS = [
  { value: '80 x 60mm', label: 'Board Size' },
  { value: 'ESP32', label: 'WiFi + BLE' },
  { value: '10A / 250V', label: 'Relay Rating' },
  { value: 'USB-C', label: 'Power Input' },
  { value: '2-Layer', label: 'PCB Stackup' },
  { value: '1.6mm', label: 'Board Thickness' },
];

const COMPONENTS = [
  { ref: 'U1', name: 'ESP32-WROOM-32', desc: 'WiFi/BLE MCU' },
  { ref: 'U2', name: 'AMS1117-3.3', desc: '3.3V LDO Regulator' },
  { ref: 'U3', name: 'CP2102N', desc: 'USB-UART Bridge' },
  { ref: 'J1', name: 'USB-C (GCT USB4105)', desc: '5V Power Input' },
  { ref: 'K1', name: 'SRD-05VDC-SL-C', desc: 'SPDT Relay 10A/250V' },
  { ref: 'J2', name: 'Terminal Block', desc: 'Relay Output' },
];

export function ModelViewerPage() {
  const ready = useModelViewerReady();
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<HTMLElement | null>(null);
  const [autoRotate, setAutoRotate] = useState(true);

  // Create the <model-viewer> element imperatively to avoid JSX type conflicts
  useEffect(() => {
    if (!ready || !containerRef.current) return;
    if (viewerRef.current) return; // already created

    const mv = document.createElement('model-viewer');
    mv.setAttribute('src', '/api/model/pcb');
    mv.setAttribute('alt', 'SafeSwitch ESP32 IoT Controller PCB');
    mv.setAttribute('auto-rotate', '');
    mv.setAttribute('auto-rotate-delay', '500');
    mv.setAttribute('rotation-per-second', '18deg');
    mv.setAttribute('camera-controls', '');
    mv.setAttribute('touch-action', 'pan-y');
    mv.setAttribute('interaction-prompt', 'auto');
    mv.setAttribute('shadow-intensity', '1.2');
    mv.setAttribute('exposure', '1.1');
    mv.setAttribute('environment-image', 'neutral');
    mv.setAttribute('camera-orbit', '45deg 65deg auto');
    mv.setAttribute('min-camera-orbit', 'auto auto 5%');
    mv.setAttribute('max-camera-orbit', 'auto auto 300%');
    mv.setAttribute('min-field-of-view', '10deg');
    mv.setAttribute('max-field-of-view', '90deg');
    mv.setAttribute('loading', 'eager');
    Object.assign(mv.style, {
      width: '100%',
      height: '65vh',
      minHeight: '400px',
      background: '#0c1614',
      display: 'block',
    });
    mv.style.setProperty('--poster-color', '#0c1614');
    mv.style.setProperty('--progress-bar-color', '#74efae');
    mv.style.setProperty('--progress-bar-height', '3px');

    containerRef.current.appendChild(mv);
    viewerRef.current = mv;

    return () => {
      mv.remove();
      viewerRef.current = null;
    };
  }, [ready]);

  // Sync auto-rotate state
  useEffect(() => {
    const mv = viewerRef.current;
    if (!mv) return;
    if (autoRotate) {
      mv.setAttribute('auto-rotate', '');
    } else {
      mv.removeAttribute('auto-rotate');
    }
  }, [autoRotate]);

  const getViewer = useCallback(() => viewerRef.current as any, []);

  const resetCamera = () => {
    const v = getViewer();
    if (!v) return;
    v.cameraOrbit = 'auto auto auto';
    v.fieldOfView = 'auto';
  };

  const zoomIn = () => {
    const v = getViewer();
    if (!v) return;
    const fov = v.getFieldOfView?.() ?? 45;
    v.fieldOfView = `${Math.max(10, fov - 5)}deg`;
  };

  const zoomOut = () => {
    const v = getViewer();
    if (!v) return;
    const fov = v.getFieldOfView?.() ?? 45;
    v.fieldOfView = `${Math.min(90, fov + 5)}deg`;
  };

  return (
    <div>
      <h1 className="page-title">
        <Box size={24} style={{ display: 'inline', marginRight: 8, verticalAlign: 'text-bottom' }} />
        3D Board Viewer
      </h1>

      {/* Viewer container */}
      <div
        style={{
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius)',
          overflow: 'hidden',
          marginBottom: 16,
          position: 'relative',
        }}
      >
        {!ready && (
          <div className="loading" style={{ height: '65vh', minHeight: 400 }}>
            Loading 3D engine...
          </div>
        )}

        <div ref={containerRef} />

        {/* Floating toolbar */}
        {ready && (
          <div
            style={{
              position: 'absolute',
              bottom: 16,
              right: 16,
              display: 'flex',
              gap: 6,
              zIndex: 10,
            }}
          >
            <button
              className="btn"
              style={{ padding: '8px', background: 'rgba(16, 32, 31, 0.85)', backdropFilter: 'blur(8px)' }}
              onClick={() => setAutoRotate(!autoRotate)}
              title={autoRotate ? 'Stop rotation' : 'Auto rotate'}
            >
              <RotateCcw size={16} style={{ color: autoRotate ? 'var(--pass)' : 'var(--muted)' }} />
            </button>
            <button
              className="btn"
              style={{ padding: '8px', background: 'rgba(16, 32, 31, 0.85)', backdropFilter: 'blur(8px)' }}
              onClick={zoomIn}
              title="Zoom in"
            >
              <ZoomIn size={16} />
            </button>
            <button
              className="btn"
              style={{ padding: '8px', background: 'rgba(16, 32, 31, 0.85)', backdropFilter: 'blur(8px)' }}
              onClick={zoomOut}
              title="Zoom out"
            >
              <ZoomOut size={16} />
            </button>
            <button
              className="btn"
              style={{ padding: '8px', background: 'rgba(16, 32, 31, 0.85)', backdropFilter: 'blur(8px)' }}
              onClick={resetCamera}
              title="Reset view"
            >
              <Maximize2 size={16} />
            </button>
          </div>
        )}
      </div>

      {/* Interaction hint */}
      <p style={{ textAlign: 'center', fontSize: 13, color: 'var(--muted)', marginBottom: 20 }}>
        Drag to rotate &bull; Scroll to zoom &bull; Right-click to pan
      </p>

      {/* Board specs */}
      <div className="card">
        <div className="card-title">Board Specifications</div>
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))',
            gap: 16,
          }}
        >
          {BOARD_SPECS.map((spec) => (
            <div key={spec.label} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 18, fontWeight: 700, color: 'var(--pass)' }}>
                {spec.value}
              </div>
              <div style={{ fontSize: 11, color: 'var(--muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                {spec.label}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Component highlights */}
      <div className="card">
        <div className="card-title">Key Components</div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          {COMPONENTS.map((comp) => (
            <div
              key={comp.ref}
              style={{
                background: 'var(--surface-strong)',
                borderRadius: 'var(--radius-sm)',
                padding: '10px 14px',
              }}
            >
              <span style={{ fontWeight: 700, color: 'var(--pass)', fontSize: 12, marginRight: 6 }}>
                {comp.ref}
              </span>
              <span style={{ fontWeight: 600, fontSize: 13 }}>{comp.name}</span>
              <div style={{ fontSize: 11, color: 'var(--muted)', marginTop: 2 }}>
                {comp.desc}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
