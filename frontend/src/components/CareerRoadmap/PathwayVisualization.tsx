'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface PathwayNode {
  stage: string;
  role: string;
  year: number;
}

interface PathwayEdge {
  from: string;
  to: string;
  skills_required: string[];
  confidence: number;
}

interface PathwayVisualizationProps {
  nodes: PathwayNode[];
  edges: PathwayEdge[];
  selectedTimeline: string;
}

const PathwayVisualization: React.FC<PathwayVisualizationProps> = ({ 
  nodes, 
  edges,
  selectedTimeline 
}) => {
  const getNodeColor = (year: number) => {
    if (year === 0) return { bg: 'bg-gray-500', ring: 'ring-gray-300' };
    if (year <= 3) return { bg: 'bg-green-500', ring: 'ring-green-300' };
    if (year <= 5) return { bg: 'bg-blue-500', ring: 'ring-blue-300' };
    return { bg: 'bg-purple-500', ring: 'ring-purple-300' };
  };

  const isNodeActive = (year: number) => {
    if (selectedTimeline === '3_year') return year <= 3;
    if (selectedTimeline === '5_year') return year <= 5;
    return true; // 10_year shows all
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-3xl shadow-xl p-8 border border-gray-200 dark:border-gray-700 overflow-hidden">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-6 text-center">
        Your Career Pathway
      </h3>

      <div className="relative">
        {/* Timeline Line */}
        <div className="absolute top-12 left-0 right-0 h-1 bg-gradient-to-r from-gray-300 via-blue-300 to-purple-300 dark:from-gray-600 dark:via-blue-600 dark:to-purple-600" />

        {/* Nodes */}
        <div className="relative flex justify-between items-start">
          {nodes.map((node, index) => {
            const colors = getNodeColor(node.year);
            const active = isNodeActive(node.year);

            return (
              <div key={node.stage} className="flex flex-col items-center" style={{ flex: 1 }}>
                {/* Node Circle */}
                <motion.div
                  className={`relative z-10 w-24 h-24 rounded-full ${active ? colors.bg : 'bg-gray-300 dark:bg-gray-600'} flex items-center justify-center ring-4 ${active ? colors.ring : 'ring-gray-200 dark:ring-gray-700'} shadow-lg`}
                  initial={{ scale: 0, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: index * 0.2, type: 'spring', stiffness: 200 }}
                  whileHover={{ scale: 1.1 }}
                >
                  <div className="text-center">
                    <div className="text-white font-bold text-sm">
                      {node.year === 0 ? 'Now' : `${node.year}Y`}
                    </div>
                  </div>
                </motion.div>

                {/* Node Label */}
                <motion.div
                  className="mt-4 text-center max-w-[120px]"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.2 + 0.1 }}
                >
                  <div className={`text-sm font-bold mb-1 ${active ? 'text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-500'}`}>
                    {node.stage}
                  </div>
                  <div className={`text-xs ${active ? 'text-gray-700 dark:text-gray-300' : 'text-gray-400 dark:text-gray-600'} line-clamp-2`}>
                    {node.role}
                  </div>
                </motion.div>

                {/* Connection Arrow */}
                {index < nodes.length - 1 && (
                  <motion.div
                    className="absolute top-12 left-1/2 w-full h-1"
                    style={{
                      left: `calc(${(index / (nodes.length - 1)) * 100}% + ${50 / nodes.length}%)`,
                      width: `calc(${100 / (nodes.length - 1)}% - ${100 / nodes.length}%)`
                    }}
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: active && isNodeActive(nodes[index + 1].year) ? 1 : 0.3 }}
                    transition={{ delay: index * 0.2 + 0.3, duration: 0.5 }}
                  />
                )}
              </div>
            );
          })}
        </div>

        {/* Skills Required (shown below) */}
        <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
            Key Transitions
          </h4>
          <div className="space-y-2">
            {edges.map((edge, index) => {
              const edgeActive = nodes.find(n => n.stage === edge.to) ? isNodeActive(nodes.find(n => n.stage === edge.to)!.year) : false;

              return (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: edgeActive ? 1 : 0.4, x: 0 }}
                  transition={{ delay: 0.5 + index * 0.1 }}
                  className={`flex items-center justify-between p-3 rounded-lg ${edgeActive ? 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-700' : 'bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700'}`}
                >
                  <div className="flex items-center space-x-2">
                    <span className={`text-xs font-semibold ${edgeActive ? 'text-blue-700 dark:text-blue-300' : 'text-gray-500 dark:text-gray-500'}`}>
                      {edge.from} → {edge.to}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="flex flex-wrap gap-1 max-w-xs">
                      {edge.skills_required.slice(0, 2).map((skill, i) => (
                        <span
                          key={i}
                          className={`px-2 py-0.5 rounded text-xs font-medium ${edgeActive ? 'bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300' : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'}`}
                        >
                          {skill}
                        </span>
                      ))}
                      {edge.skills_required.length > 2 && (
                        <span className={`px-2 py-0.5 rounded text-xs ${edgeActive ? 'text-blue-600 dark:text-blue-400' : 'text-gray-500'}`}>
                          +{edge.skills_required.length - 2}
                        </span>
                      )}
                    </div>
                    <div className={`text-xs font-bold ${edgeActive ? 'text-green-600 dark:text-green-400' : 'text-gray-500'}`}>
                      {edge.confidence}%
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PathwayVisualization;
