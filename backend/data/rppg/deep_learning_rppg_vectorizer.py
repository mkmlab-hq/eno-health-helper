#!/usr/bin/env python3
"""
딥러닝 기반 RPPG 심박수 추정 논문 데이터 벡터화 파이프라인
MKM Lab - AI 기반 한의학 진단 시스템
"""

import json
import numpy as np
import faiss
import pickle
from datetime import datetime
from typing import List, Dict, Any, Tuple
import logging
from sentence_transformers import SentenceTransformer
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deep_learning_rppg_vectorizer.log'),
        logging.StreamHandler()
    ]
)

class DeepLearningRPPGVectorizer:
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """벡터화기 초기화"""
        self.model = SentenceTransformer(model_name)
        self.vectorized_data = []
        self.ids = []
        self.stats = {
            "total_papers": 0,
            "vectorization_date": datetime.now().isoformat(),
            "model_used": model_name,
            "embedding_dimension": 384,  # all-MiniLM-L6-v2의 임베딩 차원
            "categories": {
                "cnn_3d": 0,
                "lstm": 0,
                "attention_mechanism": 0,
                "multimodal": 0,
                "transfer_learning": 0,
                "super_resolution": 0,
                "signal_quality": 0,
                "motion_artifact": 0
            }
        }
    
    def load_data(self, filename: str = "deep_learning_rppg_data.json") -> Dict[str, Any]:
        """JSON 파일에서 데이터 로드"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logging.info(f"데이터 로드 완료: {filename}")
            return data
        except FileNotFoundError:
            logging.error(f"파일을 찾을 수 없습니다: {filename}")
            return {"metadata": {}, "papers": []}
    
    def create_text_chunks(self, paper: Dict[str, Any]) -> List[Dict[str, Any]]:
        """논문을 텍스트 청크로 분할"""
        chunks = []
        
        # 제목 청크
        title_chunk = {
            "type": "title",
            "content": paper.get("title", ""),
            "paper_id": paper.get("id", ""),
            "metadata": {
                "authors": paper.get("authors", []),
                "year": paper.get("year", ""),
                "journal": paper.get("journal", ""),
                "doi": paper.get("doi", "")
            }
        }
        chunks.append(title_chunk)
        
        # 초록 청크
        abstract_chunk = {
            "type": "abstract",
            "content": paper.get("abstract", ""),
            "paper_id": paper.get("id", ""),
            "metadata": {
                "authors": paper.get("authors", []),
                "year": paper.get("year", ""),
                "journal": paper.get("journal", ""),
                "doi": paper.get("doi", "")
            }
        }
        chunks.append(abstract_chunk)
        
        # 방법론 청크
        if "methodology" in paper:
            methodology_chunk = {
                "type": "methodology",
                "content": paper.get("methodology", ""),
                "paper_id": paper.get("id", ""),
                "metadata": {
                    "authors": paper.get("authors", []),
                    "year": paper.get("year", ""),
                    "journal": paper.get("journal", ""),
                    "doi": paper.get("doi", "")
                }
            }
            chunks.append(methodology_chunk)
        
        # 키워드 청크
        if "keywords" in paper:
            keywords_chunk = {
                "type": "keywords",
                "content": ", ".join(paper.get("keywords", [])),
                "paper_id": paper.get("id", ""),
                "metadata": {
                    "authors": paper.get("authors", []),
                    "year": paper.get("year", ""),
                    "journal": paper.get("journal", ""),
                    "doi": paper.get("doi", "")
                }
            }
            chunks.append(keywords_chunk)
        
        # 성능 지표 청크
        if "performance" in paper:
            performance_text = ", ".join([f"{k}: {v}" for k, v in paper.get("performance", {}).items()])
            performance_chunk = {
                "type": "performance",
                "content": performance_text,
                "paper_id": paper.get("id", ""),
                "metadata": {
                    "authors": paper.get("authors", []),
                    "year": paper.get("year", ""),
                    "journal": paper.get("journal", ""),
                    "doi": paper.get("doi", "")
                }
            }
            chunks.append(performance_chunk)
        
        # 특징 청크
        if "features" in paper:
            features_chunk = {
                "type": "features",
                "content": ", ".join(paper.get("features", [])),
                "paper_id": paper.get("id", ""),
                "metadata": {
                    "authors": paper.get("authors", []),
                    "year": paper.get("year", ""),
                    "journal": paper.get("journal", ""),
                    "doi": paper.get("doi", "")
                }
            }
            chunks.append(features_chunk)
        
        # 응용 분야 청크
        if "applications" in paper:
            applications_chunk = {
                "type": "applications",
                "content": ", ".join(paper.get("applications", [])),
                "paper_id": paper.get("id", ""),
                "metadata": {
                    "authors": paper.get("authors", []),
                    "year": paper.get("year", ""),
                    "journal": paper.get("journal", ""),
                    "doi": paper.get("doi", "")
                }
            }
            chunks.append(applications_chunk)
        
        return chunks
    
    def vectorize_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """텍스트 청크들을 벡터화"""
        vectorized_chunks = []
        
        for i, chunk in enumerate(chunks):
            try:
                # 텍스트 벡터화
                text = chunk["content"]
                if not text.strip():
                    continue
                
                embedding = self.model.encode(text, convert_to_tensor=False)
                
                vectorized_chunk = {
                    "id": f"{chunk['paper_id']}_{chunk['type']}_{i}",
                    "paper_id": chunk["paper_id"],
                    "type": chunk["type"],
                    "content": text,
                    "embedding": embedding.tolist(),
                    "metadata": chunk["metadata"]
                }
                
                vectorized_chunks.append(vectorized_chunk)
                self.ids.append(vectorized_chunk["id"])
                
                logging.info(f"청크 벡터화 완료: {vectorized_chunk['id']}")
                
            except Exception as e:
                logging.error(f"청크 벡터화 실패: {chunk.get('id', 'unknown')} - {str(e)}")
                continue
        
        return vectorized_chunks
    
    def process_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """논문들을 처리하여 벡터화"""
        all_vectorized_chunks = []
        
        for paper in papers:
            try:
                # 논문을 청크로 분할
                chunks = self.create_text_chunks(paper)
                
                # 청크들을 벡터화
                vectorized_chunks = self.vectorize_chunks(chunks)
                
                all_vectorized_chunks.extend(vectorized_chunks)
                self.stats["total_papers"] += 1
                
                # 카테고리 카운트 업데이트
                keywords = paper.get("keywords", [])
                if "cnn_3d" in keywords:
                    self.stats["categories"]["cnn_3d"] += 1
                if "lstm" in keywords:
                    self.stats["categories"]["lstm"] += 1
                if "attention_mechanism" in keywords:
                    self.stats["categories"]["attention_mechanism"] += 1
                if "multimodal" in keywords:
                    self.stats["categories"]["multimodal"] += 1
                if "transfer_learning" in keywords:
                    self.stats["categories"]["transfer_learning"] += 1
                if "super_resolution" in keywords:
                    self.stats["categories"]["super_resolution"] += 1
                if "signal_quality" in keywords:
                    self.stats["categories"]["signal_quality"] += 1
                if "motion_artifact" in keywords:
                    self.stats["categories"]["motion_artifact"] += 1
                
                logging.info(f"논문 처리 완료: {paper.get('title', 'Unknown')}")
                
            except Exception as e:
                logging.error(f"논문 처리 실패: {paper.get('title', 'Unknown')} - {str(e)}")
                continue
        
        return all_vectorized_chunks
    
    def create_faiss_index(self, vectorized_data: List[Dict[str, Any]]) -> faiss.Index:
        """FAISS 인덱스 생성"""
        if not vectorized_data:
            logging.error("벡터화된 데이터가 없습니다.")
            return None
        
        # 임베딩 벡터들을 numpy 배열로 변환
        embeddings = np.array([chunk["embedding"] for chunk in vectorized_data], dtype=np.float32)
        
        # FAISS 인덱스 생성 (L2 거리 사용)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        
        # 인덱스에 벡터 추가
        index.add(embeddings)
        
        logging.info(f"FAISS 인덱스 생성 완료: {index.ntotal}개 벡터")
        return index
    
    def save_vectorized_data(self, vectorized_data: List[Dict[str, Any]], 
                           filename: str = "vectorized_deep_learning_rppg_data.json"):
        """벡터화된 데이터를 JSON 파일로 저장"""
        output_data = {
            "metadata": self.stats,
            "vectorized_chunks": vectorized_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logging.info(f"벡터화된 데이터 저장 완료: {filename}")
    
    def save_faiss_index(self, index: faiss.Index, filename: str = "deep_learning_rppg_index.faiss"):
        """FAISS 인덱스를 파일로 저장"""
        faiss.write_index(index, filename)
        logging.info(f"FAISS 인덱스 저장 완료: {filename}")
    
    def save_ids(self, filename: str = "deep_learning_rppg_ids.pkl"):
        """ID 리스트를 pickle 파일로 저장"""
        with open(filename, 'wb') as f:
            pickle.dump(self.ids, f)
        logging.info(f"ID 리스트 저장 완료: {filename}")
    
    def save_stats(self, filename: str = "deep_learning_rppg_vectorization_stats.json"):
        """통계 정보를 별도 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
        
        logging.info(f"통계 저장 완료: {filename}")
    
    def run_vectorization_pipeline(self, input_file: str = "deep_learning_rppg_data.json"):
        """전체 벡터화 파이프라인 실행"""
        logging.info("딥러닝 기반 RPPG 심박수 추정 논문 벡터화 파이프라인 시작")
        
        # 1. 데이터 로드
        data = self.load_data(input_file)
        papers = data.get("papers", [])
        
        if not papers:
            logging.error("처리할 논문이 없습니다.")
            return
        
        # 2. 논문 처리 및 벡터화
        vectorized_data = self.process_papers(papers)
        
        if not vectorized_data:
            logging.error("벡터화된 데이터가 없습니다.")
            return
        
        # 3. FAISS 인덱스 생성
        index = self.create_faiss_index(vectorized_data)
        
        if index is None:
            logging.error("FAISS 인덱스 생성 실패")
            return
        
        # 4. 결과 저장
        self.save_vectorized_data(vectorized_data)
        self.save_faiss_index(index)
        self.save_ids()
        self.save_stats()
        
        logging.info("딥러닝 기반 RPPG 심박수 추정 논문 벡터화 파이프라인 완료")
        logging.info(f"총 {len(vectorized_data)}개 청크 벡터화됨")
        logging.info(f"총 {self.stats['total_papers']}개 논문 처리됨")

def main():
    """메인 실행 함수"""
    vectorizer = DeepLearningRPPGVectorizer()
    vectorizer.run_vectorization_pipeline()

if __name__ == "__main__":
    main() 