import { useState, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Upload, RotateCw, AlertCircle, X, ChevronRight, Sparkles, Clock } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { motion, AnimatePresence } from 'framer-motion';

const ClockDetector = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [detectedTime, setDetectedTime] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [confidence, setConfidence] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);

  // Animation variants
  const letterAnimation = {
    hidden: { y: 20, opacity: 0 },
    visible: i => ({
      y: 0,
      opacity: 1,
      transition: {
        delay: i * 0.1,
      }
    })
  };

  const floatingAnimation = {
    y: [0, -10, 0],
    transition: {
      duration: 4,
      repeat: Infinity,
      ease: "easeInOut"
    }
  };

  const pulseAnimation = {
    scale: [1, 1.02, 1],
    opacity: [0.5, 0.8, 0.5],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: "easeInOut"
    }
  };

  const orbitAnimation = {
    rotate: [0, 360],
    transition: {
      duration: 20,
      repeat: Infinity,
      ease: "linear"
    }
  };

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

  const appName = "ClockSense AI";

  return (
    <div className="fixed inset-0 bg-black flex flex-col items-center justify-center overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div 
          className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(76,29,149,0.2),rgba(0,0,0,0.9))]"
          animate={pulseAnimation}
        />
      </div>

      {/* Orbital Particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={`orbit-${i}`}
            className="absolute left-1/2 top-1/2 w-[600px] h-[600px] rounded-full border border-purple-500/10"
            style={{
              transform: `translate(-50%, -50%) rotate(${i * 45}deg)`,
            }}
            animate={orbitAnimation}
            transition={{
              duration: 20 + i * 5,
              repeat: Infinity,
              ease: "linear"
            }}
          >
            <motion.div
              className="absolute w-2 h-2 bg-purple-500/30 rounded-full"
              style={{
                top: '0%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
              }}
            />
          </motion.div>
        ))}
      </div>

      {/* Floating Particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-purple-500/20 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [-20, 20],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      {/* App Name */}
      <motion.div
        className="text-center mb-12"
        initial="hidden"
        animate="visible"
      >
        <div className="flex items-center justify-center gap-3 mb-2">
          <motion.div
            animate={{
              rotate: [0, 360],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              ease: "linear"
            }}
          >
            <Clock className="w-8 h-8 text-purple-400" />
          </motion.div>
          <div className="flex">
            {appName.split('').map((letter, i) => (
              <motion.span
                key={i}
                custom={i}
                variants={letterAnimation}
                className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-fuchsia-400 bg-clip-text text-transparent"
              >
                {letter}
              </motion.span>
            ))}
          </div>
        </div>
        <motion.p
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="text-purple-300 text-sm"
        >
          Upload an analog clock image to detect the time
        </motion.p>
      </motion.div>

      {/* Main Content */}
      <motion.div 
        className="relative flex flex-col items-center"
        animate={floatingAnimation}
      >
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
          whileHover={{ boxShadow: "0 0 30px rgba(147, 51, 234, 0.3)" }}
        >
          {!selectedImage ? (
            <motion.label
              htmlFor="image-upload"
              className="absolute inset-4 rounded-full cursor-pointer overflow-hidden group"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <motion.div 
                className="absolute inset-0 bg-purple-800/20 backdrop-blur-sm flex flex-col items-center justify-center p-8 text-center"
                whileHover={{
                  backgroundColor: "rgba(147, 51, 234, 0.3)",
                }}
              >
                <motion.div
                  animate={{
                    y: [0, -10, 0],
                    transition: {
                      duration: 2,
                      repeat: Infinity,
                      ease: "easeInOut"
                    }
                  }}
                >
                  <Upload className="w-16 h-16 text-purple-400 mb-4" />
                </motion.div>
                <p className="text-xl text-purple-200 mb-2">Drop your clock image</p>
                <p className="text-sm text-purple-300">or click to browse</p>
              </motion.div>
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
              <motion.img
                src={previewUrl}
                alt="Clock preview"
                className="w-full h-full object-cover"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300 }}
              />
            </motion.div>
          )}

          {/* Detect Button */}
          {selectedImage && (
            <motion.div
              initial={{ x: 50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ type: "spring", stiffness: 200 }}
            >
              <Button
                className="absolute -right-20 top-1/2 -translate-y-1/2 rounded-full bg-gradient-to-r from-purple-600 to-fuchsia-600 w-10 h-10 p-0"
                onClick={detectTime}
                disabled={!selectedImage || isLoading}
              >
                {isLoading ? (
                  <RotateCw className="w-5 h-5 animate-spin" />
                ) : (
                  <motion.div
                    animate={{
                      x: [0, 5, 0],
                      transition: {
                        duration: 1,
                        repeat: Infinity,
                      }
                    }}
                  >
                    <ChevronRight className="w-5 h-5" />
                  </motion.div>
                )}
              </Button>
            </motion.div>
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
              whileHover={{ scale: 1.02 }}
              transition={{ type: "spring", stiffness: 400 }}
            >
              <motion.div 
                className="bg-purple-900/30 backdrop-blur-xl rounded-2xl p-6 border border-purple-500/30"
                whileHover={{
                  boxShadow: "0 0 30px rgba(147, 51, 234, 0.2)",
                  borderColor: "rgba(147, 51, 234, 0.5)",
                }}
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <motion.div
                      animate={{
                        rotate: [0, 360],
                        transition: {
                          duration: 3,
                          repeat: Infinity,
                          ease: "linear"
                        }
                      }}
                    >
                      <Sparkles className="w-5 h-5 text-purple-400" />
                    </motion.div>
                    <h3 className="text-lg font-semibold text-purple-200">Detection Results</h3>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-purple-300 hover:text-white hover:bg-purple-800/50"
                    onClick={resetDetection}
                  >
                    <motion.div whileHover={{ rotate: 90 }}>
                      <X className="w-4 h-4" />
                    </motion.div>
                  </Button>
                </div>

                <div className="text-center mb-6">
                  <motion.p 
                    className="text-5xl font-bold bg-gradient-to-r from-purple-300 to-fuchsia-300 bg-clip-text text-transparent"
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{
                      type: "spring",
                      stiffness: 500,
                      damping: 30
                    }}
                  >
                    {String(detectedTime.hours).padStart(2, '0')}:
                    {String(detectedTime.minutes).padStart(2, '0')}:
                    {String(detectedTime.seconds).padStart(2, '0')}
                  </motion.p>
                </div>

                {confidence && (
                  <motion.div 
                    className="space-y-2"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                  >
                    <div className="flex justify-between text-sm text-purple-200">
                      <span>AI Confidence</span>
                      <span className="font-semibold">{(confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="relative h-2 bg-purple-900/50 rounded-full overflow-hidden">
                      <motion.div
                        className="absolute inset-y-0 left-0 bg-gradient-to-r from-purple-500 to-fuchsia-500"
                        initial={{ width: 0 }}
                        animate={{ width: `${confidence * 100}%` }}
                        transition={{ duration: 1, ease: "easeOut" }}
                      />
                    </div>
                  </motion.div>
                )}

                {error && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ type: "spring" }}
                  >
                    <Alert variant="destructive" className="mt-4 bg-red-900/50 border-red-500/50 text-red-200">
                      <AlertCircle className="w-4 h-4 mr-2" />
                      <AlertDescription>{error}</AlertDescription>
                    </Alert>
                  </motion.div>
                )}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
};

export default ClockDetector;