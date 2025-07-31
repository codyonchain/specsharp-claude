import { useState, useEffect } from 'react';
import { X, Download, FileText, FileSpreadsheet, Image as ImageIcon } from 'lucide-react';
import { tradePackageService } from '../services/api';
import './TradePackageModal.css';

interface TradePackageModalProps {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
  trade: string;
  onGenerate: (projectId: string, trade: string) => Promise<any>;
}

function TradePackageModal({ isOpen, onClose, projectId, trade, onGenerate }: TradePackageModalProps) {
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState<any>(null);
  const [packageData, setPackageData] = useState<any>(null);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    if (isOpen && projectId && trade) {
      loadPreview();
    }
  }, [isOpen, projectId, trade]);

  const loadPreview = async () => {
    try {
      setLoading(true);
      setError('');
      console.log(`[TradePackageModal] Loading preview for trade: ${trade}, project: ${projectId}`);
      
      const data = await tradePackageService.getPreview(projectId, trade);
      console.log(`[TradePackageModal] Preview loaded successfully:`, data);
      setPreview(data.preview);
    } catch (err: any) {
      console.error('[TradePackageModal] Error loading preview:', err);
      
      let errorMessage = 'Failed to load preview';
      
      if (err.response) {
        // The request was made and the server responded with a status code
        if (err.response.status === 404) {
          errorMessage = 'Trade package feature is not available yet. Please check back later.';
        } else if (err.response.status === 401) {
          errorMessage = 'Authentication required. Please log in again.';
        } else if (err.response.data?.detail) {
          errorMessage = err.response.data.detail;
        } else {
          errorMessage = `Server error (${err.response.status}). Please try again later.`;
        }
      } else if (err.request) {
        // The request was made but no response was received
        errorMessage = 'Unable to connect to the server. Please check your connection.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setLoading(true);
      setError('');
      console.log(`[TradePackageModal] Starting package generation...`);
      
      // Set a timeout for the generation
      const timeoutId = setTimeout(() => {
        setError('Package generation is taking longer than expected. Please try again.');
        setLoading(false);
      }, 30000); // 30 seconds timeout
      
      try {
        const data = await onGenerate(projectId, trade);
        clearTimeout(timeoutId);
        
        console.log(`[TradePackageModal] Package generated successfully:`, data);
        
        if (!data || !data.package) {
          throw new Error('Invalid response format - missing package data');
        }
        
        setPackageData(data.package);
      } catch (err) {
        clearTimeout(timeoutId);
        throw err;
      }
    } catch (err: any) {
      console.error('[TradePackageModal] Error generating package:', err);
      setError(err.message || 'Failed to generate package');
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = (base64Data: string, filename: string, mimeType: string) => {
    try {
      const byteCharacters = atob(base64Data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      const blob = new Blob([byteArray], { type: mimeType });
      
      const url = URL.createObjectURL(blob);
      
      // Check if we're on a mobile device
      const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
      
      if (isMobile) {
        // Mobile-specific handling
        if (mimeType === 'application/pdf') {
          // For PDFs, open in a new window/tab which allows viewing and saving
          const newWindow = window.open(url, '_blank');
          if (!newWindow) {
            // Fallback if popup blocked
            window.location.href = url;
          }
        } else {
          // For other files, create a link and use different click method
          const link = document.createElement('a');
          link.href = url;
          link.download = filename;
          link.style.display = 'none';
          document.body.appendChild(link);
          
          // Use dispatchEvent for better mobile compatibility
          const clickEvent = new MouseEvent('click', {
            view: window,
            bubbles: true,
            cancelable: false
          });
          link.dispatchEvent(clickEvent);
          
          document.body.removeChild(link);
        }
      } else {
        // Desktop browser - use standard method
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
      
      // Clean up the object URL after a delay
      setTimeout(() => URL.revokeObjectURL(url), 250);
    } catch (error) {
      console.error('[TradePackageModal] Download failed:', error);
      alert(`Failed to download ${filename}. Please try again.`);
    }
  };

  const handleDownloadPDF = () => {
    if (packageData?.pdf) {
      downloadFile(packageData.pdf, `${trade}_package_${projectId}.pdf`, 'application/pdf');
    }
  };

  const handleDownloadCSV = () => {
    if (packageData?.csv) {
      downloadFile(packageData.csv, `${trade}_data_${projectId}.csv`, 'text/csv');
    }
  };

  const handleDownloadSchematic = () => {
    if (packageData?.schematic) {
      const base64Data = packageData.schematic.split(',')[1];
      downloadFile(base64Data, `${trade}_schematic_${projectId}.png`, 'image/png');
    }
  };

  const handleDownloadAll = async () => {
    const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    
    if (isMobile) {
      // On mobile, add delays between downloads to ensure they process correctly
      handleDownloadPDF();
      await new Promise(resolve => setTimeout(resolve, 500));
      handleDownloadCSV();
      await new Promise(resolve => setTimeout(resolve, 500));
      handleDownloadSchematic();
    } else {
      // On desktop, download all at once
      handleDownloadPDF();
      handleDownloadCSV();
      handleDownloadSchematic();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content trade-package-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{trade.toUpperCase()} Trade Package</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={24} />
          </button>
        </div>

        <div className="modal-body">
          {loading && (
            <div className="loading-state">
              <div className="spinner"></div>
              <p>Preparing trade package...</p>
              <p className="loading-hint">This may take up to 30 seconds</p>
            </div>
          )}

          {error && (
            <div className="error-message">
              <p className="error-text">{error}</p>
              <div className="error-actions">
                <button className="retry-btn" onClick={() => {
                  setError('');
                  if (!preview) {
                    loadPreview();
                  } else if (!packageData) {
                    handleGenerate();
                  }
                }}>Retry</button>
                <button className="cancel-btn" onClick={onClose}>Cancel</button>
              </div>
            </div>
          )}

          {preview && !loading && (
            <div className="preview-container">
              <div className="preview-header">
                <h3>Package Preview</h3>
                {!packageData && (
                  <button className="generate-btn" onClick={handleGenerate}>
                    Generate Full Package
                  </button>
                )}
              </div>

              <div className="preview-content">
                <div className="preview-summary">
                  <div className="summary-item">
                    <label>Trade Total:</label>
                    <span className="value">${preview.total_cost?.toLocaleString()}</span>
                  </div>
                  <div className="summary-item">
                    <label>Categories:</label>
                    <span className="value">{preview.categories?.length || 0}</span>
                  </div>
                  <div className="summary-item">
                    <label>Systems:</label>
                    <span className="value">
                      {preview.categories?.reduce((sum: number, cat: any) => sum + cat.system_count, 0) || 0}
                    </span>
                  </div>
                </div>

                {preview.categories?.map((category: any) => (
                  <div key={category.name} className="category-preview">
                    <h4>{category.name}</h4>
                    <div className="category-info">
                      <span>Subtotal: ${category.subtotal?.toLocaleString()}</span>
                      <span>{category.system_count} systems</span>
                    </div>
                    <div className="systems-preview">
                      {category.systems?.map((system: any, idx: number) => (
                        <div key={idx} className="system-item">
                          <span>{system.name}</span>
                          <span>${system.total_cost?.toLocaleString()}</span>
                        </div>
                      ))}
                      {category.system_count > 3 && (
                        <p className="more-items">...and {category.system_count - 3} more</p>
                      )}
                    </div>
                  </div>
                ))}

                {preview.schematic_preview && (
                  <div className="schematic-preview">
                    <h4>Trade Schematic Preview</h4>
                    <img src={preview.schematic_preview} alt={`${trade} schematic`} />
                  </div>
                )}
              </div>
            </div>
          )}

          {packageData && (
            <div className="download-section">
              <h3>Package Ready for Download</h3>
              <div className="download-options">
                <button className="download-btn" onClick={handleDownloadPDF}>
                  <FileText size={20} />
                  Download PDF Report
                </button>
                <button className="download-btn" onClick={handleDownloadCSV}>
                  <FileSpreadsheet size={20} />
                  Download CSV Data
                </button>
                <button className="download-btn" onClick={handleDownloadSchematic}>
                  <ImageIcon size={20} />
                  Download Schematic
                </button>
              </div>
              <button className="download-all-btn" onClick={handleDownloadAll}>
                <Download size={20} />
                Download All Files
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default TradePackageModal;