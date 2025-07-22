import { useState, useEffect } from 'react';
import { X, Download, FileText, FileSpreadsheet, Image as ImageIcon } from 'lucide-react';
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
      const response = await fetch(`http://localhost:8001/api/v1/trade-package/preview/${projectId}/${trade}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to load preview');
      
      const data = await response.json();
      setPreview(data.preview);
    } catch (err: any) {
      setError(err.message || 'Failed to load preview');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async () => {
    try {
      setLoading(true);
      setError('');
      const data = await onGenerate(projectId, trade);
      setPackageData(data.package);
    } catch (err: any) {
      setError(err.message || 'Failed to generate package');
    } finally {
      setLoading(false);
    }
  };

  const downloadFile = (base64Data: string, filename: string, mimeType: string) => {
    const byteCharacters = atob(base64Data);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: mimeType });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
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

  const handleDownloadAll = () => {
    handleDownloadPDF();
    handleDownloadCSV();
    handleDownloadSchematic();
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
            </div>
          )}

          {error && (
            <div className="error-message">
              <p>{error}</p>
              <button onClick={loadPreview}>Retry</button>
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