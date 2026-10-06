/**
 * EcoSort AI - Primary Waste Analyzer Page (Stage 6).
 * Orchestrates multimodal input (Take Photo / Upload Image / Text Description),
 * loading states, and result rendering.
 */

import React, { useState } from 'react';
import {
  Sparkles,
  Camera,
  UploadCloud,
  FileText,
  AlertCircle,
  RefreshCw,
} from 'lucide-react';
import { classifyImage, classifyText } from '../api/classify';
import type { ClassificationResultResponse } from '../types/api';
import { ImageUploader } from '../components/analyze/ImageUploader';
import { TextInput } from '../components/analyze/TextInput';
import { LoadingState } from '../components/analyze/LoadingState';
import { ResultCard } from '../components/analyze/ResultCard';
import { Button } from '../components/common/Button';
import { Card } from '../components/common/Card';
import type { AnalyzeMode } from '../types/navigation';

export type { AnalyzeMode };

interface AnalyzePageProps {
  initialMode?: AnalyzeMode;
}

export const AnalyzePage: React.FC<AnalyzePageProps> = ({ initialMode = 'camera' }) => {
  const [inputMode, setInputMode] = useState<AnalyzeMode>(initialMode);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [textDescription, setTextDescription] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [result, setResult] = useState<ClassificationResultResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [prevMode, setPrevMode] = useState<AnalyzeMode>(initialMode);
  if (initialMode !== prevMode) {
    setPrevMode(initialMode);
    setInputMode(initialMode);
  }

  const isImageMode = inputMode === 'camera' || inputMode === 'upload';

  const handleAnalyze = async () => {
    setErrorMessage(null);

    if (isImageMode) {
      if (!selectedFile) {
        setErrorMessage(
          inputMode === 'camera'
            ? 'Please take or capture a photo of the waste item.'
            : 'Please select or upload an image of the waste item.'
        );
        return;
      }
    } else {
      if (!textDescription.trim()) {
        setErrorMessage('Please enter a description of the household item.');
        return;
      }
      if (textDescription.trim().length < 2) {
        setErrorMessage('Description must be at least 2 characters.');
        return;
      }
    }

    setIsLoading(true);
    try {
      let response: ClassificationResultResponse;
      if (isImageMode && selectedFile) {
        response = await classifyImage(selectedFile);
      } else {
        response = await classifyText(textDescription.trim());
      }
      setResult(response);
    } catch (err: any) {
      setErrorMessage(
        err.message || 'An unexpected error occurred while analyzing the waste item. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setTextDescription('');
    setResult(null);
    setErrorMessage(null);
  };

  const modeButtons: { id: AnalyzeMode; label: string; icon: React.ReactNode }[] = [
    { id: 'camera', label: 'Take a Photo', icon: <Camera size={16} /> },
    { id: 'upload', label: 'Upload Image', icon: <UploadCloud size={16} /> },
    { id: 'text', label: 'Text Description', icon: <FileText size={16} /> },
  ];

  return (
    <div style={{ maxWidth: '860px', margin: '0 auto', display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Header Introduction */}
      <div>
        <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '-0.02em' }}>
          Analyze Household Waste
        </h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
          Capture a photo with your camera, upload an existing image, or describe the item to receive deterministic disposal, preparation, and safety guidance.
        </p>
      </div>

      {/* When analysis result is present */}
      {result ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button variant="outline" size="sm" icon={<RefreshCw size={14} />} onClick={handleReset}>
              Analyze Another Item
            </Button>
          </div>
          <ResultCard result={result} onReset={handleReset} />
        </div>
      ) : isLoading ? (
        <LoadingState />
      ) : (
        /* Input Form Card */
        <Card padding="lg">
          {/* Mode Switcher Tabs supporting Camera, Upload & Text */}
          <div
            style={{
              display: 'flex',
              backgroundColor: 'var(--bg-surface-secondary)',
              borderRadius: 'var(--radius-md)',
              padding: '4px',
              marginBottom: '20px',
              border: '1px solid var(--border-subtle)',
              gap: '4px',
            }}
          >
            {modeButtons.map((btn) => {
              const isActive = inputMode === btn.id;
              return (
                <button
                  key={btn.id}
                  type="button"
                  onClick={() => {
                    setInputMode(btn.id);
                    setErrorMessage(null);
                  }}
                  style={{
                    flex: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                    padding: '10px 14px',
                    borderRadius: 'var(--radius-sm)',
                    fontSize: '0.875rem',
                    fontWeight: isActive ? 600 : 500,
                    color: isActive ? 'var(--brand-green)' : 'var(--text-secondary)',
                    backgroundColor: isActive ? 'var(--bg-surface)' : 'transparent',
                    boxShadow: isActive ? 'var(--shadow-sm)' : 'none',
                    transition: 'all var(--transition-fast)',
                    border: 'none',
                    cursor: 'pointer',
                  }}
                >
                  {btn.icon}
                  <span>{btn.label}</span>
                </button>
              );
            })}
          </div>

          {/* Form Content based on active mode */}
          <div style={{ marginBottom: '24px' }}>
            {isImageMode ? (
              <ImageUploader
                selectedFile={selectedFile}
                onSelectFile={setSelectedFile}
                activeMethod={inputMode as 'camera' | 'upload'}
                onChangeMethod={(method) => setInputMode(method)}
                disabled={isLoading}
              />
            ) : (
              <TextInput
                value={textDescription}
                onChange={setTextDescription}
                disabled={isLoading}
              />
            )}
          </div>

          {/* Error Banner */}
          {errorMessage && (
            <div
              style={{
                padding: '12px 16px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                color: 'var(--status-danger)',
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                fontSize: '0.875rem',
                marginBottom: '20px',
              }}
            >
              <AlertCircle size={18} style={{ flexShrink: 0 }} />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Primary Action Button */}
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <Button
              variant="primary"
              size="lg"
              icon={<Sparkles size={18} />}
              onClick={handleAnalyze}
              disabled={
                isLoading ||
                (isImageMode && !selectedFile) ||
                (!isImageMode && !textDescription.trim())
              }
              style={{ minWidth: '180px' }}
            >
              Analyze Waste
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};
