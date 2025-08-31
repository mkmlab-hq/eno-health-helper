"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Progress } from '@/components/ui/Progress';
import { Badge } from '@/components/ui/Badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/Tabs';
import {
  Activity,
  Heart,
  Mic,
  Brain,
  Sparkles,
  Lightbulb,
  TrendingUp,
  User,
  Zap
} from 'lucide-react';

interface MKM12Forces {
  K: number;  // Solar force
  L: number;  // Lesser Yang force
  S: number;  // Lesser Yin force
  M: number;  // Greater Yin force
}

interface MKM12Personas {
  A1: number; // Solar Mode
  A2: number; // Yang Mode
  A3: number; // Yin Mode
}

interface MKM12Analysis {
  dominant_persona: string;
  persona_balance: number;
  force_balance: number;
  overall_state: string;
}

interface MKM12Data {
  forces: MKM12Forces;
  personas: MKM12Personas;
  analysis: MKM12Analysis;
  digital_fingerprint: string;
  narrative: {
    title: string;
    summary: string;
    overall: string;
    recommendations: string[];
  };
}

const MKM12Dashboard: React.FC = () => {
  const [mkm12Data, setMkm12Data] = useState<MKM12Data | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');

  // Sample data for demonstration
  const sampleData: MKM12Data = {
    forces: {
      K: 0.75, // Solar force - High energy
      L: 0.65, // Lesser Yang force - Good stability
      S: 0.45, // Lesser Yin force - Moderate emotion
      M: 0.55  // Greater Yin force - Balanced wisdom
    },
    personas: {
      A1: 0.45, // Solar Mode - Leadership
      A2: 0.35, // Yang Mode - Teamwork
      A3: 0.20  // Yin Mode - Intuition
    },
    analysis: {
      dominant_persona: "A1",
      persona_balance: 0.75,
      force_balance: 0.70,
      overall_state: "Balanced"
    },
    digital_fingerprint: "a1b2c3d4e5f6...",
    narrative: {
      title: "MKM12 분석 결과",
      summary: "현재 A1 페르소나가 가장 활성화되어 있습니다.",
      overall: "전반적으로 균형 잡힌 상태입니다. 각 힘이 조화롭게 작용하고 있어 안정적인 컨디션을 유지하고 있습니다.",
      recommendations: [
        "태양적 힘이 높습니다. 에너지 소모가 클 수 있으니 적절한 휴식을 취하세요.",
        "태양적 페르소나가 활성화되어 있습니다. 리더십과 창의성을 발휘할 좋은 기회입니다.",
        "전체적인 균형을 위해 명상, 운동, 충분한 휴식을 권장합니다."
      ]
    }
  };

  useEffect(() => {
    // Load sample data for demonstration
    setMkm12Data(sampleData);
  }, []);

  const getForceColor = (force: keyof MKM12Forces) => {
    const colors = {
      K: 'bg-blue-500',
      L: 'bg-purple-500',
      S: 'bg-orange-500',
      M: 'bg-green-500'
    };
    return colors[force];
  };

  const getForceName = (force: keyof MKM12Forces) => {
    const names = {
      K: '태양적 힘 (Solar)',
      L: '소양적 힘 (Lesser Yang)',
      S: '소음적 힘 (Lesser Yin)',
      M: '태음적 힘 (Greater Yin)'
    };
    return names[force];
  };

  const getPersonaName = (persona: keyof MKM12Personas) => {
    const names = {
      A1: '태양적 모드 (Solar Mode)',
      A2: '양적 모드 (Yang Mode)',
      A3: '음적 모드 (Yin Mode)'
    };
    return names[persona];
  };

  const getPersonaColor = (persona: keyof MKM12Personas) => {
    const colors = {
      A1: 'bg-blue-500',
      A2: 'bg-purple-500',
      A3: 'bg-orange-500'
    };
    return colors[persona];
  };

  const getStateColor = (state: string) => {
    switch (state) {
      case 'Balanced':
        return 'bg-green-100 text-green-800';
      case 'Unbalanced':
        return 'bg-red-100 text-red-800';
      case 'Moderate':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (!mkm12Data) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">MKM12 데이터를 로딩 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 text-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
            MKM12 대시보드
          </h1>
          <p className="text-xl text-gray-300">
            당신의 고유한 행동 패턴을 MKM12 이론으로 분석합니다
          </p>
        </div>

        {/* Main Dashboard */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-slate-800/50">
            <TabsTrigger value="overview" className="data-[state=active]:bg-blue-600">
              <Activity className="w-4 h-4 mr-2" />
              개요
            </TabsTrigger>
            <TabsTrigger value="forces" className="data-[state=active]:bg-blue-600">
              <Zap className="w-4 h-4 mr-2" />
              4가지 힘
            </TabsTrigger>
            <TabsTrigger value="personas" className="data-[state=active]:bg-blue-600">
              <User className="w-4 h-4 mr-2" />
              페르소나
            </TabsTrigger>
            <TabsTrigger value="insights" className="data-[state=active]:bg-blue-600">
              <Lightbulb className="w-4 h-4 mr-2" />
              인사이트
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Overall State */}
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg flex items-center">
                    <Sparkles className="w-5 h-5 mr-2 text-blue-400" />
                    전체 상태
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Badge className={`${getStateColor(mkm12Data.analysis.overall_state)} text-sm`}>
                    {mkm12Data.analysis.overall_state}
                  </Badge>
                  <p className="text-sm text-gray-300 mt-2">
                    {mkm12Data.narrative.overall}
                  </p>
                </CardContent>
              </Card>

              {/* Dominant Persona */}
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg flex items-center">
                    <User className="w-5 h-5 mr-2 text-purple-400" />
                    주요 페르소나
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-purple-400 mb-2">
                    {mkm12Data.analysis.dominant_persona}
                  </div>
                  <p className="text-sm text-gray-300">
                    {getPersonaName(mkm12Data.analysis.dominant_persona as keyof MKM12Personas)}
                  </p>
                </CardContent>
              </Card>

              {/* Force Balance */}
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg flex items-center">
                    <TrendingUp className="w-5 h-5 mr-2 text-green-400" />
                    힘의 균형
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Progress
                    value={mkm12Data.analysis.force_balance * 100}
                    className="mb-2"
                  />
                  <p className="text-sm text-gray-300">
                    {(mkm12Data.analysis.force_balance * 100).toFixed(1)}%
                  </p>
                </CardContent>
              </Card>

              {/* Persona Balance */}
              <Card className="bg-slate-800/50 border-slate-700">
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg flex items-center">
                    <Brain className="w-5 h-5 mr-2 text-orange-400" />
                    페르소나 균형
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <Progress
                    value={mkm12Data.analysis.persona_balance * 100}
                    className="mb-2"
                  />
                  <p className="text-sm text-gray-300">
                    {(mkm12Data.analysis.persona_balance * 100).toFixed(1)}%
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Digital Fingerprint */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Sparkles className="w-5 h-5 mr-2 text-blue-400" />
                  디지털 지문
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="bg-slate-900 p-4 rounded-lg font-mono text-sm">
                  {mkm12Data.digital_fingerprint}
                </div>
                <p className="text-sm text-gray-400 mt-2">
                  이 고유한 패턴은 당신만의 MKM12 특성을 나타냅니다
                </p>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Forces Tab */}
          <TabsContent value="forces" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {Object.entries(mkm12Data.forces).map(([force, value]) => (
                <Card key={force} className="bg-slate-800/50 border-slate-700">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <div className={`w-4 h-4 rounded-full ${getForceColor(force as keyof MKM12Forces)} mr-3`}></div>
                      {getForceName(force as keyof MKM12Forces)}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold mb-4">
                      {(value * 100).toFixed(1)}%
                    </div>
                    <Progress value={value * 100} className="mb-4" />
                    <div className="text-sm text-gray-300">
                      {force === 'K' && '에너지와 활력의 태양적 힘'}
                      {force === 'L' && '안정성과 균형의 소양적 힘'}
                      {force === 'S' && '감정 표현의 소음적 힘'}
                      {force === 'M' && '지혜와 성찰의 태음적 힘'}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Personas Tab */}
          <TabsContent value="personas" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {Object.entries(mkm12Data.personas).map(([persona, value]) => (
                <Card key={persona} className="bg-slate-800/50 border-slate-700">
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <div className={`w-4 h-4 rounded-full ${getPersonaColor(persona as keyof MKM12Personas)} mr-3`}></div>
                      {getPersonaName(persona as keyof MKM12Personas)}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="text-3xl font-bold mb-4">
                      {(value * 100).toFixed(1)}%
                    </div>
                    <Progress value={value * 100} className="mb-4" />
                    <div className="text-sm text-gray-300">
                      {persona === 'A1' && '리더십과 창의성을 발휘하는 태양적 모드'}
                      {persona === 'A2' && '팀워크와 협력을 중시하는 양적 모드'}
                      {persona === 'A3' && '직관과 감성을 활용하는 음적 모드'}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Insights Tab */}
          <TabsContent value="insights" className="space-y-6">
            {/* Recommendations */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Lightbulb className="w-5 h-5 mr-2 text-yellow-400" />
                  맞춤형 권장사항
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mkm12Data.narrative.recommendations.map((rec, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-slate-700/50 rounded-lg">
                      <div className="w-2 h-2 bg-blue-400 rounded-full mt-2 flex-shrink-0"></div>
                      <p className="text-sm text-gray-200">{rec}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Summary */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Brain className="w-5 h-5 mr-2 text-purple-400" />
                  분석 요약
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-200 mb-4">{mkm12Data.narrative.summary}</p>
                <p className="text-gray-300">{mkm12Data.narrative.overall}</p>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4 mt-8">
          <Button
            className="bg-blue-600 hover:bg-blue-700"
            onClick={() => setActiveTab('overview')}
          >
            <Activity className="w-4 h-4 mr-2" />
            전체 보기
          </Button>
          <Button
            className="bg-purple-600 hover:bg-purple-700"
            onClick={() => setActiveTab('forces')}
          >
            <Zap className="w-4 h-4 mr-2" />
            힘 분석
          </Button>
          <Button
            className="bg-orange-600 hover:bg-orange-700"
            onClick={() => setActiveTab('personas')}
          >
            <User className="w-4 h-4 mr-2" />
            페르소나
          </Button>
        </div>
      </div>
    </div>
  );
};

export default MKM12Dashboard;
