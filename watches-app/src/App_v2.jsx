import { useState, useCallback, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Upload, RotateCw, AlertCircle, X, ChevronRight, Sparkles } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { motion, AnimatePresence } from 'framer-motion';

const ClockDetector = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [detectedTime, setDetectedTime] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [timeString, setTimeString] = useState('');
  const [isExpanded, setIsExpanded] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      const now = new Date();
      setTimeString(now.toLocaleTimeString());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  const handleImageUpload = useCallback((event) => {
    const file = event.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      setPreviewUrl(URL.createObjectURL(file));
      setDetectedTime(null);
      setError(null);
      setConfidence(null);
      setIsExpanded(true);
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
        } else if (typeof data.detail === 'string') {
          errorMessage = data.detail;
        }
        throw new Error(errorMessage);
      }
      
      setDetectedTime(data.time);
      setConfidence(data.confidence);
    } catch (error) {
      setError(error.message);
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
    setIsExpanded(false);
  }, []);

  return (
    <div className="fixed inset-0 bg-black flex flex-col items-center justify-center overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(76,29,149,0.2),rgba(0,0,0,0.9))]" />
      </div>

      {/* Current Time Display */}
      <motion.div
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        className="text-4xl font-mono text-purple-300 mb-8"
      >
        {timeString}
      </motion.div>

      {/* Main Content */}
      <div className="relative flex flex-col items-center">
        {/* Upload Circle */}
        <motion.div
          className={`relative w-96 h-96 rounded-full ${
            selectedImage ? 'bg-purple-900/20' : 'bg-purple-900/10'
          } backdrop-blur-xl border border-purple-500/30 flex items-center justify-center transition-all duration-500`}
          animate={{
            scale: isExpanded ? [1, 1.1, 1] : 1,
            rotate: isExpanded ? [0, 10, 0] : 0
          }}
          transition={{ duration: 0.5 }}
        >
          {!selectedImage ? (
            <motion.label
              htmlFor="image-upload"
              className="absolute inset-4 rounded-full cursor-pointer overflow-hidden group"
              whileHover={{ scale: 1.05 }}
            >
              <div className="absolute inset-0 bg-purple-800/20 backdrop-blur-sm flex flex-col items-center justify-center p-8 text-center">
                <Upload className="w-16 h-16 text-purple-400 mb-4" />
                <p className="text-xl text-purple-200 mb-2">Drop your clock image</p>
                <p className="text-sm text-purple-300">or click to browse</p>
              </div>
              <input
                type="file"
                id="image-upload"
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
            </motion.label>
          ) : (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="absolute inset-4 rounded-full overflow-hidden"
            >
              <img
                src={previewUrl}
                alt="Clock preview"
                className="w-full h-full object-cover"
              />
            </motion.div>
          )}

          {/* Detect Button */}
          {selectedImage && (
            <Button
              className="absolute -right-20 top-1/2 -translate-y-1/2 rounded-full bg-gradient-to-r from-purple-600 to-fuchsia-600 w-10 h-10 p-0"
              onClick={detectTime}
              disabled={!selectedImage || isLoading}
            >
              {isLoading ? <RotateCw className="w-5 h-5 animate-spin" /> : <ChevronRight className="w-5 h-5" />}
            </Button>
          )}
        </motion.div>

        {/* Results Panel */}
        <AnimatePresence>
          {detectedTime && (
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 20, opacity: 0 }}
              className="w-full max-w-xl mt-8"
            >
              <div className="bg-purple-900/30 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/30">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-purple-400" />
                    <h3 className="text-lg font-semibold text-purple-200">Detection Results</h3>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-purple-300 hover:text-white hover:bg-purple-800/50"
                    onClick={resetDetection}
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>

                <div className="text-center mb-6">
                  <motion.p 
                    className="text-5xl font-bold bg-gradient-to-r from-purple-300 to-fuchsia-300 bg-clip-text text-transparent"
                    initial={{ scale: 0.8 }}
                    animate={{ scale: 1 }}
                  >
                    {String(detectedTime.hours).padStart(2, '0')}:
                    {String(detectedTime.minutes).padStart(2, '0')}:
                    {String(detectedTime.seconds).padStart(2, '0')}
                  </motion.p>
                </div>

                {confidence && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm text-purple-200">
                      <span>AI Confidence</span>
                      <span className="font-semibold">{(confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="relative h-2 bg-purple-900/50 rounded-full overflow-hidden">
                      <motion.div
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-fuchsia-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${confidence * 100}%` }}
                        transition={{ duration: 1 }}
                      />
                    </div>
                  </div>
                )}

                {error && (
                  <Alert variant="destructive" className="mt-4 bg-red-900/50 border-red-500/50 text-red-200">
                    <AlertCircle className="w-4 h-4 mr-2" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default ClockDetector;