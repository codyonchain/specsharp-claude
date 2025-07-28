import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, TrendingUp, Clock, DollarSign } from 'lucide-react';

interface SuccessAnimationProps {
  show: boolean;
  onClose: () => void;
  milestone?: 'first' | 'tenth' | 'hundredth';
  projectName?: string;
  savingsAmount?: number;
}

export const SuccessAnimation: React.FC<SuccessAnimationProps> = ({
  show,
  onClose,
  milestone = 'first',
  projectName,
  savingsAmount
}) => {
  useEffect(() => {
    if (show) {
      const timer = setTimeout(() => {
        onClose();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [show, onClose]);

  const getMilestoneContent = () => {
    switch (milestone) {
      case 'first':
        return {
          icon: CheckCircle,
          title: "First Estimate Saved!",
          subtitle: "You're already saving time and money.",
          color: "bg-green-500"
        };
      case 'tenth':
        return {
          icon: TrendingUp,
          title: "10 Estimates Created!",
          subtitle: "Your efficiency is through the roof!",
          color: "bg-blue-500"
        };
      case 'hundredth':
        return {
          icon: DollarSign,
          title: "100 Estimates Strong!",
          subtitle: savingsAmount ? `Estimated ${savingsAmount.toLocaleString()} hours saved!` : "You're a SpecSharp power user!",
          color: "bg-purple-500"
        };
      default:
        return {
          icon: CheckCircle,
          title: "Success!",
          subtitle: projectName || "Your estimate has been saved.",
          color: "bg-green-500"
        };
    }
  };

  const content = getMilestoneContent();
  const Icon = content.icon;

  return (
    <AnimatePresence>
      {show && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
            onClick={onClose}
          >
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              exit={{ scale: 0, rotate: 180 }}
              transition={{
                type: "spring",
                stiffness: 260,
                damping: 20
              }}
              className={`${content.color} text-white p-8 rounded-2xl shadow-2xl max-w-md mx-4`}
              onClick={(e) => e.stopPropagation()}
            >
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2 }}
              >
                <Icon className="w-20 h-20 mx-auto mb-4" />
              </motion.div>
              
              <motion.h2
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="text-3xl font-bold text-center mb-2"
              >
                {content.title}
              </motion.h2>
              
              <motion.p
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.4 }}
                className="text-lg text-center opacity-90"
              >
                {content.subtitle}
              </motion.p>

              {milestone === 'first' && (
                <motion.div
                  initial={{ y: 20, opacity: 0 }}
                  animate={{ y: 0, opacity: 1 }}
                  transition={{ delay: 0.5 }}
                  className="mt-6 flex justify-center space-x-4"
                >
                  <div className="flex items-center">
                    <Clock className="w-5 h-5 mr-2" />
                    <span className="text-sm">Time saved</span>
                  </div>
                  <div className="flex items-center">
                    <DollarSign className="w-5 h-5 mr-2" />
                    <span className="text-sm">Cost optimized</span>
                  </div>
                </motion.div>
              )}

              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.6 }}
                className="mt-6 flex justify-center"
              >
                <div className="w-2 h-2 bg-white rounded-full mx-1 animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-white rounded-full mx-1 animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-white rounded-full mx-1 animate-bounce" style={{ animationDelay: '300ms' }} />
              </motion.div>
            </motion.div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

// Mini success notification for quick feedback
export const MiniSuccessNotification: React.FC<{
  message: string;
  show: boolean;
  onClose: () => void;
}> = ({ message, show, onClose }) => {
  useEffect(() => {
    if (show) {
      const timer = setTimeout(() => {
        onClose();
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [show, onClose]);

  return (
    <AnimatePresence>
      {show && (
        <motion.div
          initial={{ x: 300, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: 300, opacity: 0 }}
          className="fixed bottom-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-2 z-50"
        >
          <CheckCircle className="w-5 h-5" />
          <span>{message}</span>
        </motion.div>
      )}
    </AnimatePresence>
  );
};