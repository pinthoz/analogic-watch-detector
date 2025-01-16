import { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Clock, Upload, RotateCw, AlertCircle, X } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { motion, AnimatePresence } from 'framer-motion';

const ClockDetector = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [detectedTime, setDetectedTime] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [detectionImage, setDetectionImage] = useState(null);

  const handleImageUpload = useCallback((event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setDetectedTime(null);
      setError(null);
      setConfidence(null);
      setDetectionImage(null);
    }
  }, []);
  
  const detectTime = async () => {
    setIsLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', selectedImage);
    
    try {
      const response = await fetch('http://127.0.0.1:8000/api/detect-time', {
        method: 'POST',
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
        let errorMessage = 'An error occurred while detecting the time';
        
        if (data.detail && typeof data.detail === 'object') {
          errorMessage = data.detail.message;
          console.error('Error details: ', data.detail.technical_details);
        } else if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        }
        
        throw new Error(errorMessage);
      }
      
      setDetectedTime(data.time);
      setConfidence(data.confidence);
      setDetectionImage(data.detectionImage);
    } catch (error) {
      setError(error.message);
      console.error('Error in detection: ', error);
    } finally {
      setIsLoading(false);
    }
  };

  const resetDetection = useCallback(() => {
    setSelectedImage(null);
    setPreviewUrl(null);
    setDetectedTime(null);
    setError(null);
    setConfidence(null);
    setDetectionImage(null);
  }, []);

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-purple-950 via-violet-900 to-fuchsia-900 text-white">
      {/* Header with Glassmorphism */}
      <motion.div 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="absolute top-0 left-0 right-0 p-4 flex justify-between items-center bg-purple-950/30 backdrop-blur-lg border-b border-purple-500/20 z-10"
      >
        <motion.div 
          className="flex items-center gap-3"
          whileHover={{ scale: 1.02 }}
        >
          <Clock className="w-6 h-6 text-purple-400" />
          <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-fuchsia-400 bg-clip-text text-transparent">
            Analogic Watch Detector
          </h1>
        </motion.div>
        <Button
          variant="ghost"
          size="sm"
          className="text-purple-300 hover:text-white hover:bg-purple-800/50"
          onClick={resetDetection}
        >
          <X className="w-4 h-4" />
        </Button>
      </motion.div>

      {/* Main Content */}
      <div className="fixed inset-0 pt-16 flex">
        {/* Left Panel - Preview Area */}
        <div className="relative flex-1 flex items-center justify-center p-8">
          <AnimatePresence mode="wait">
            {!selectedImage ? (
              <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="w-full max-w-lg"
              >
                <label 
                  htmlFor="image-upload" 
                  className="block p-12 border-2 border-dashed border-purple-500/50 rounded-2xl bg-purple-900/20 hover:bg-purple-800/30 transition-all duration-300 cursor-pointer text-center backdrop-blur-sm hover:shadow-2xl hover:shadow-purple-500/20"
                >
                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    transition={{ type: "spring", stiffness: 400, damping: 10 }}
                  >
                    <Upload className="w-16 h-16 mx-auto mb-4 text-purple-400" />
                    <p className="text-xl text-purple-200 mb-3">Drop your clock image here</p>
                    <p className="text-sm text-purple-300">or click to browse files</p>
                  </motion.div>
                  <input
                    type="file"
                    id="image-upload"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                </label>
              </motion.div>
            ) : (
              <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="relative w-full h-full flex items-center justify-center"
              >
                <motion.img 
                  initial={{ scale: 0.8 }}
                  animate={{ scale: 1 }}
                  src={previewUrl} 
                  alt="Clock preview" 
                  className="max-w-full max-h-full object-contain rounded-2xl shadow-2xl shadow-purple-500/20"
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Right Panel - Results Overlay with Glassmorphism */}
        <motion.div 
          initial={{ x: 100 }}
          animate={{ x: 0 }}
          className="w-96 h-full bg-purple-950/40 backdrop-blur-xl border-l border-purple-500/20 flex flex-col"
        >
          <div className="flex-1 p-6 overflow-y-auto">
            <Button 
              onClick={detectTime} 
              disabled={!selectedImage || isLoading}
              className="w-full bg-gradient-to-r from-purple-600 to-fuchsia-600 hover:from-purple-500 hover:to-fuchsia-500 mb-6 h-12 text-lg font-medium shadow-lg shadow-purple-500/20"
            >
              {isLoading ? (
                <motion.div
                  className="flex items-center justify-center"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  <RotateCw className="w-5 h-5 animate-spin mr-2" />
                  Detecting...
                </motion.div>
              ) : (
                <motion.div
                  className="flex items-center justify-center"
                  whileHover={{ scale: 1.02 }}
                >
                  <Clock className="w-5 h-5 mr-2" />
                  Detect Time
                </motion.div>
              )}
            </Button>

            <AnimatePresence mode="wait">
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                >
                  <Alert variant="destructive" className="bg-red-900/50 border-red-500/50 text-red-200">
                    <AlertCircle className="w-4 h-4 mr-2" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                </motion.div>
              )}

              {detectedTime && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="space-y-8"
                >
                  <motion.div 
                    className="p-6 bg-gradient-to-br from-purple-600/20 to-fuchsia-600/20 rounded-2xl backdrop-blur-sm border border-purple-500/20 shadow-lg"
                    whileHover={{ scale: 1.02 }}
                    transition={{ type: "spring", stiffness: 400, damping: 10 }}
                  >
                    <p className="text-5xl font-bold mb-2 tracking-wider text-center bg-gradient-to-r from-purple-300 to-fuchsia-300 bg-clip-text text-transparent">
                      {String(detectedTime.hours).padStart(2, '0')}:
                      {String(detectedTime.minutes).padStart(2, '0')}:
                      {String(detectedTime.seconds).padStart(2, '0')}
                    </p>
                    <p className="text-sm text-center text-purple-300">Detected Time</p>
                  </motion.div>

                  {confidence && (
                    <motion.div 
                      className="space-y-2"
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.2 }}
                    >
                      <div className="flex justify-between text-sm text-purple-200">
                        <span>Confidence</span>
                        <span className="font-semibold">{(confidence * 100).toFixed(1)}%</span>
                      </div>
                      <Progress 
                        value={confidence * 100} 
                        className="h-2 bg-purple-900/50"
                      />
                    </motion.div>
                  )}

                  {detectionImage && (
                    <motion.div 
                      className="rounded-2xl overflow-hidden shadow-lg shadow-purple-500/20"
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 }}
                    >
                      <img 
                        src={detectionImage} 
                        alt="Detection visualization" 
                        className="w-full"
                      />
                    </motion.div>
                  )}
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default ClockDetector;