/**
 * EcoSort AI - Image Uploader & Device Camera Capture Component (Stage 6).
 * Supports front camera (webcam), rear camera, device enumeration & camera selection,
 * live viewfinder with mirror toggle, hardware diagnostics, and unified preview controls.
 */

import React, { useRef, useState, useEffect, useCallback } from 'react';
import {
  UploadCloud,
  Camera,
  Image as ImageIcon,
  RefreshCw,
  Trash2,
  X,
  Smartphone,
  Video,
  AlertCircle,
  HelpCircle,
} from 'lucide-react';
import { Button } from '../common/Button';

interface ImageUploaderProps {
  selectedFile: File | null;
  onSelectFile: (file: File | null) => void;
  activeMethod: 'camera' | 'upload';
  onChangeMethod?: (method: 'camera' | 'upload') => void;
  disabled?: boolean;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  selectedFile,
  onSelectFile,
  activeMethod,
  onChangeMethod,
  disabled = false,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isCameraStarting, setIsCameraStarting] = useState(false);
  const [cameraFacing, setCameraFacing] = useState<'user' | 'environment'>('user');
  const [videoDevices, setVideoDevices] = useState<MediaDeviceInfo[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<string>('');
  const [showTroubleshooting, setShowTroubleshooting] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const stopLiveCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
    setIsCameraActive(false);
  }, []);

  const refreshDevices = useCallback(async () => {
    if (!navigator.mediaDevices?.enumerateDevices) return;
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoInputs = devices.filter((d) => d.kind === 'videoinput');
      setVideoDevices(videoInputs);
      if (videoInputs.length > 0 && !selectedDeviceId) {
        // Automatically prefer physical camera over virtual cameras (like VCam)
        const physicalCam = videoInputs.find(
          (d) =>
            !d.label.toLowerCase().includes('vcam') &&
            !d.label.toLowerCase().includes('virtual') &&
            !d.label.toLowerCase().includes('obs')
        );
        setSelectedDeviceId(physicalCam ? physicalCam.deviceId : videoInputs[0].deviceId);
      }
    } catch (err) {
      console.warn('enumerateDevices error:', err);
    }
  }, [selectedDeviceId]);

  // Manage object URL lifecycle for clean garbage collection
  useEffect(() => {
    if (selectedFile) {
      const url = URL.createObjectURL(selectedFile);
      setPreviewUrl(url);
      return () => {
        URL.revokeObjectURL(url);
      };
    } else {
      setPreviewUrl(null);
    }
  }, [selectedFile]);

  // Clean up camera stream on unmount
  useEffect(() => {
    return () => {
      stopLiveCamera();
    };
  }, [stopLiveCamera]);

  useEffect(() => {
    refreshDevices();
  }, [refreshDevices]);

  const validateAndSetFile = (file: File) => {
    setErrorMessage(null);

    // Validate size (max 5 MB matching backend MAX_UPLOAD_SIZE_MB)
    if (file.size > 5 * 1024 * 1024) {
      setErrorMessage('Image size exceeds 5MB limit. Please select a smaller photo.');
      return;
    }

    // Validate type (JPEG, PNG, WEBP)
    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
    if (!validTypes.includes(file.type.toLowerCase()) && !file.name.match(/\.(jpg|jpeg|png|webp)$/i)) {
      setErrorMessage('Unsupported image format. Please upload JPEG, PNG, or WEBP.');
      return;
    }

    stopLiveCamera();
    onSelectFile(file);
  };

  const startLiveCamera = async (targetDeviceId?: string, facing: 'user' | 'environment' = cameraFacing) => {
    setErrorMessage(null);
    setIsCameraStarting(true);
    stopLiveCamera();

    const devId = targetDeviceId !== undefined ? targetDeviceId : selectedDeviceId;

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      setIsCameraStarting(false);
      setErrorMessage(
        'Direct camera access is not supported in this browser context. Please use the system camera app or upload an image.'
      );
      cameraInputRef.current?.click();
      return;
    }

    try {
      let stream: MediaStream;

      if (devId) {
        try {
          stream = await navigator.mediaDevices.getUserMedia({
            video: { deviceId: { exact: devId } },
            audio: false,
          });
        } catch {
          // If exact device ID failed, try ideal or facingMode
          stream = await navigator.mediaDevices.getUserMedia({
            video: { deviceId: { ideal: devId } },
            audio: false,
          });
        }
      } else {
        try {
          stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: { ideal: facing } },
            audio: false,
          });
        } catch {
          // Fallback: any video camera available
          stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false,
          });
        }
      }

      streamRef.current = stream;
      setCameraFacing(facing);
      setIsCameraActive(true);

      // Re-enumerate to get labeled camera names once permission is active
      refreshDevices();

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.muted = true;
        videoRef.current.play().catch((err) => console.warn('Video play error:', err));
      }
    } catch (err: any) {
      console.warn('Camera access failed:', err);
      stopLiveCamera();
      setShowTroubleshooting(true);

      if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
        setErrorMessage(
          'Camera access was denied by your browser. Please allow camera permissions in your address bar (look for the camera or lock icon).'
        );
      } else if (err.name === 'NotReadableError' || err.name === 'TrackStartError') {
        setErrorMessage(
          'Your camera is currently in use by another application (like Zoom, Teams, VCam, or Windows Camera). Please close other camera apps and try again.'
        );
      } else if (err.name === 'NotFoundError' || err.name === 'DevicesNotFoundError') {
        setErrorMessage(
          'No working physical camera hardware detected. If using a laptop, check if the physical webcam privacy slider/switch is turned on.'
        );
      } else {
        setErrorMessage(
          `Unable to open camera (${err.name || 'error'}). Please select your physical webcam from the dropdown or use the system camera button.`
        );
      }
    } finally {
      setIsCameraStarting(false);
    }
  };

  const handleDeviceChange = (deviceId: string) => {
    setSelectedDeviceId(deviceId);
    if (isCameraActive) {
      startLiveCamera(deviceId);
    }
  };

  const handleFlipCamera = () => {
    const nextFacing = cameraFacing === 'user' ? 'environment' : 'user';
    setCameraFacing(nextFacing);
    startLiveCamera(undefined, nextFacing);
  };

  const handleCaptureFromVideo = () => {
    if (!videoRef.current) return;
    const video = videoRef.current;
    const width = video.videoWidth || 1280;
    const height = video.videoHeight || 720;

    const canvas = document.createElement('canvas');
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Mirror image if front camera is active
    if (cameraFacing === 'user') {
      ctx.translate(width, 0);
      ctx.scale(-1, 1);
    }
    ctx.drawImage(video, 0, 0, width, height);

    canvas.toBlob(
      (blob) => {
        if (blob) {
          const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
          const file = new File([blob], `photo-${cameraFacing}-${timestamp}.jpg`, { type: 'image/jpeg' });
          validateAndSetFile(file);
        }
      },
      'image/jpeg',
      0.92
    );
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    if (!disabled) setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (disabled) return;

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleRetake = () => {
    onSelectFile(null);
    if (onChangeMethod) {
      onChangeMethod('camera');
    }
    startLiveCamera();
  };

  const handleReplace = () => {
    fileInputRef.current?.click();
  };

  const handleRemove = () => {
    stopLiveCamera();
    onSelectFile(null);
    setErrorMessage(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  return (
    <div>
      {/* Hidden native file & camera capture inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/jpg"
        style={{ display: 'none' }}
        onChange={handleFileChange}
        disabled={disabled}
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture={cameraFacing}
        style={{ display: 'none' }}
        onChange={handleFileChange}
        disabled={disabled}
      />

      {/* 1. UNIFIED IMAGE PREVIEW: Shown after either Taking a Photo or Uploading an Image */}
      {selectedFile && previewUrl ? (
        <div
          style={{
            position: 'relative',
            borderRadius: 'var(--radius-lg)',
            overflow: 'hidden',
            border: '1px solid var(--border-default)',
            backgroundColor: 'var(--bg-surface-secondary)',
          }}
        >
          <div
            style={{
              maxHeight: '380px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              backgroundColor: '#0a0d0b',
              overflow: 'hidden',
            }}
          >
            <img
              src={previewUrl}
              alt="Selected waste item preview"
              style={{
                maxWidth: '100%',
                maxHeight: '380px',
                objectFit: 'contain',
              }}
            />
          </div>

          {/* Bottom Bar with Retake / Replace / Remove Controls */}
          <div
            style={{
              padding: '12px 16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '12px',
              backgroundColor: 'var(--bg-surface)',
              borderTop: '1px solid var(--border-default)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', minWidth: '180px', overflow: 'hidden' }}>
              <ImageIcon size={16} color="var(--brand-green)" style={{ flexShrink: 0 }} />
              <div style={{ fontSize: '0.8125rem', color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                <span style={{ fontWeight: 600 }}>{selectedFile.name}</span>
                <span style={{ color: 'var(--text-muted)', marginLeft: '6px' }}>
                  ({(selectedFile.size / 1024).toFixed(0)} KB)
                </span>
              </div>
            </div>

            {/* Exactly the 3 requested controls */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Button
                variant="outline"
                size="sm"
                icon={<Camera size={14} />}
                onClick={handleRetake}
                disabled={disabled}
                title="Retake photo using camera"
              >
                Retake
              </Button>

              <Button
                variant="outline"
                size="sm"
                icon={<RefreshCw size={13} />}
                onClick={handleReplace}
                disabled={disabled}
                title="Replace with an existing image from files"
              >
                Replace
              </Button>

              <Button
                variant="danger"
                size="sm"
                icon={<Trash2 size={14} />}
                onClick={handleRemove}
                disabled={disabled}
                title="Remove image"
              >
                Remove
              </Button>
            </div>
          </div>
        </div>
      ) : activeMethod === 'camera' ? (
        /* 2. TAKE A PHOTO SECTION (Device Camera where supported) */
        isCameraActive ? (
          /* Live Camera Viewfinder */
          <div
            style={{
              position: 'relative',
              borderRadius: 'var(--radius-lg)',
              overflow: 'hidden',
              backgroundColor: '#000000',
              border: '2px solid var(--brand-green)',
            }}
          >
            <video
              ref={(node) => {
                videoRef.current = node;
                if (node && streamRef.current && node.srcObject !== streamRef.current) {
                  node.srcObject = streamRef.current;
                  node.muted = true;
                  node.play().catch((err) => console.warn('Video play error:', err));
                }
              }}
              autoPlay
              playsInline
              muted
              style={{
                width: '100%',
                maxHeight: '400px',
                objectFit: 'cover',
                display: 'block',
                transform: cameraFacing === 'user' ? 'scaleX(-1)' : 'none',
              }}
            />

            {/* Viewfinder Overlay Controls */}
            <div
              style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                padding: '16px',
                background: 'linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0) 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '8px',
              }}
            >
              <Button
                variant="ghost"
                size="sm"
                icon={<X size={16} />}
                onClick={stopLiveCamera}
                style={{ color: '#ffffff' }}
              >
                Cancel
              </Button>

              <Button
                variant="primary"
                size="md"
                icon={<Camera size={16} />}
                onClick={handleCaptureFromVideo}
                style={{ padding: '10px 24px', fontWeight: 600 }}
              >
                Capture Photo
              </Button>

              <Button
                variant="ghost"
                size="sm"
                icon={<RefreshCw size={14} />}
                onClick={handleFlipCamera}
                style={{ color: '#ffffff', fontSize: '0.75rem' }}
                title={`Switch camera`}
              >
                {cameraFacing === 'user' ? 'Rear Cam' : 'Front Cam'}
              </Button>
            </div>
          </div>
        ) : (
          /* Camera Launch Prompt with Camera Selector and Troubleshooting */
          <div
            style={{
              border: '2px dashed var(--border-default)',
              borderRadius: 'var(--radius-lg)',
              padding: '36px 20px',
              textAlign: 'center',
              backgroundColor: 'var(--bg-surface-secondary)',
            }}
          >
            <div
              style={{
                width: '56px',
                height: '56px',
                borderRadius: '50%',
                backgroundColor: 'var(--brand-green-muted)',
                color: 'var(--brand-green)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px',
              }}
            >
              <Camera size={28} />
            </div>

            <h4 style={{ fontSize: '1.0625rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '6px' }}>
              Take a Photo with Camera
            </h4>
            <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', maxWidth: '420px', margin: '0 auto 16px' }}>
              Hold your waste item in front of your front camera/webcam, or switch to your device camera app.
            </p>

            {/* Camera Device Selector if multiple devices exist */}
            {videoDevices.length > 0 && (
              <div
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '18px',
                  padding: '6px 12px',
                  borderRadius: 'var(--radius-md)',
                  backgroundColor: 'var(--bg-surface)',
                  border: '1px solid var(--border-default)',
                }}
              >
                <Video size={14} color="var(--brand-green)" />
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Camera:</span>
                <select
                  value={selectedDeviceId}
                  onChange={(e) => handleDeviceChange(e.target.value)}
                  style={{
                    backgroundColor: 'transparent',
                    color: 'var(--text-primary)',
                    border: 'none',
                    fontSize: '0.8125rem',
                    fontWeight: 500,
                    outline: 'none',
                    cursor: 'pointer',
                  }}
                >
                  {videoDevices.map((d, idx) => (
                    <option key={d.deviceId || idx} value={d.deviceId} style={{ backgroundColor: 'var(--bg-surface)' }}>
                      {d.label || `Camera ${idx + 1}`}
                    </option>
                  ))}
                </select>
              </div>
            )}

            {/* Action Buttons */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', flexWrap: 'wrap' }}>
              <Button
                variant="primary"
                size="md"
                icon={<Camera size={16} />}
                onClick={() => startLiveCamera(selectedDeviceId, 'user')}
                disabled={disabled}
                isLoading={isCameraStarting}
              >
                Start Camera
              </Button>

              <Button
                variant="outline"
                size="md"
                icon={<Smartphone size={16} />}
                onClick={() => cameraInputRef.current?.click()}
                disabled={disabled}
                title="Open device camera or select photo from device"
              >
                System Camera App
              </Button>
            </div>

            {/* Helper link to switch to file upload */}
            {onChangeMethod && (
              <div style={{ marginTop: '16px', fontSize: '0.8125rem' }}>
                <span style={{ color: 'var(--text-muted)' }}>Already have a picture? </span>
                <button
                  type="button"
                  onClick={() => onChangeMethod('upload')}
                  style={{
                    color: 'var(--brand-green)',
                    fontWeight: 600,
                    textDecoration: 'underline',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                  }}
                >
                  Upload an existing image instead
                </button>
              </div>
            )}

            {/* Diagnostic Troubleshooting Card */}
            <div style={{ marginTop: '20px' }}>
              <button
                type="button"
                onClick={() => setShowTroubleshooting((prev) => !prev)}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  fontSize: '0.75rem',
                  cursor: 'pointer',
                }}
              >
                <HelpCircle size={13} />
                <span>Camera not opening? Click here for troubleshooting</span>
              </button>

              {showTroubleshooting && (
                <div
                  style={{
                    marginTop: '12px',
                    padding: '14px 18px',
                    borderRadius: 'var(--radius-md)',
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-default)',
                    fontSize: '0.75rem',
                    color: 'var(--text-secondary)',
                    textAlign: 'left',
                    lineHeight: 1.6,
                  }}
                >
                  <div style={{ fontWeight: 600, color: 'var(--brand-green)', marginBottom: '6px' }}>
                    Webcam &amp; Front Camera Diagnostic Guide:
                  </div>
                  <ul style={{ paddingLeft: '18px', margin: 0, display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <li>
                      <strong>1. Physical HP Camera Switch / Slider:</strong> Many HP laptops have a physical privacy slider over the lens or an electrical toggle switch on the side/keyboard (e.g. <code>Fn+F10</code> or <code>Fn+F12</code>) that powers off the camera hardware. Verify the shutter is open.
                    </li>
                    <li>
                      <strong>2. Windows Privacy Settings:</strong> Open Windows <em>Settings &gt; Privacy &amp; security &gt; Camera</em> and verify that <em>"Camera access"</em> and <em>"Let desktop apps access your camera"</em> are turned <strong>ON</strong>.
                    </li>
                    <li>
                      <strong>3. Browser Address Bar:</strong> Click the padlock / tune icon next to <code>localhost:5173</code> in your browser address bar to ensure camera permission is set to <strong>"Allow"</strong>.
                    </li>
                    <li>
                      <strong>4. Virtual Camera Conflicts:</strong> If <em>VCam</em> or <em>OBS</em> is installed, select your physical webcam from the dropdown above.
                    </li>
                    <li>
                      <strong>5. Mobile Phone Testing:</strong> Open <code>http://10.246.93.121:5173</code> on your mobile phone or tablet on the same Wi-Fi network to use your phone's camera directly!
                    </li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        )
      ) : (
        /* 3. UPLOAD EXISTING IMAGE SECTION */
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => !disabled && fileInputRef.current?.click()}
          style={{
            border: `2px dashed ${isDragging ? 'var(--brand-green)' : 'var(--border-default)'}`,
            borderRadius: 'var(--radius-lg)',
            padding: '40px 20px',
            textAlign: 'center',
            backgroundColor: isDragging ? 'var(--brand-green-muted)' : 'var(--bg-surface-secondary)',
            cursor: disabled ? 'not-allowed' : 'pointer',
            transition: 'all var(--transition-fast)',
          }}
          className="upload-dropzone"
        >
          <div
            style={{
              width: '56px',
              height: '56px',
              borderRadius: '50%',
              backgroundColor: 'var(--brand-green-muted)',
              color: 'var(--brand-green)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px',
            }}
          >
            <UploadCloud size={28} />
          </div>

          <h4 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '4px' }}>
            Upload Waste Photo or Drag & Drop
          </h4>
          <p style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginBottom: '18px' }}>
            Supports JPEG, PNG, or WEBP (Max 10MB)
          </p>

          <div
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px' }}
            onClick={(e) => e.stopPropagation()}
          >
            <Button
              variant="outline"
              size="md"
              icon={<UploadCloud size={16} />}
              onClick={() => fileInputRef.current?.click()}
              disabled={disabled}
            >
              Browse Files
            </Button>
          </div>

          {onChangeMethod && (
            <div style={{ marginTop: '18px', fontSize: '0.8125rem' }} onClick={(e) => e.stopPropagation()}>
              <span style={{ color: 'var(--text-muted)' }}>Want to snap a new photo? </span>
              <button
                type="button"
                onClick={() => onChangeMethod('camera')}
                style={{
                  color: 'var(--brand-green)',
                  fontWeight: 600,
                  textDecoration: 'underline',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                }}
              >
                Take a photo with camera
              </button>
            </div>
          )}
        </div>
      )}

      {/* Error message banner */}
      {errorMessage && (
        <div
          style={{
            marginTop: '14px',
            padding: '12px 16px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            color: 'var(--status-danger)',
            fontSize: '0.8125rem',
            textAlign: 'left',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '8px',
          }}
        >
          <AlertCircle size={16} style={{ flexShrink: 0, marginTop: '2px' }} />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
};
