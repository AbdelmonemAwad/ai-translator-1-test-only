#!/usr/bin/env python3
"""
AI Integration Workaround for Python 3.11
حل بديل لتكامل الذكاء الاصطناعي مع Python 3.11

This module provides alternative implementations for AI libraries that have version conflicts.
"""

import os
import sys
import logging
import subprocess
import json
import requests
from typing import Dict, List, Optional, Any
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

class FastWhisperIntegration:
    """تكامل Faster-Whisper كبديل لـ OpenAI Whisper"""
    
    def __init__(self):
        self.model_cache = {}
        self.available = False
        self._check_availability()
    
    def _check_availability(self):
        """فحص توفر faster-whisper"""
        try:
            import faster_whisper
            self.available = True
            logger.info("✓ Faster-Whisper available")
        except ImportError:
            logger.warning("⚠ Faster-Whisper not available")
            self.available = False
    
    def load_model(self, model_size: str = "base"):
        """تحميل نموذج Whisper"""
        if not self.available:
            raise ImportError("Faster-Whisper not available")
        
        if model_size in self.model_cache:
            return self.model_cache[model_size]
        
        try:
            from faster_whisper import WhisperModel
            
            # تحميل النموذج
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
            self.model_cache[model_size] = model
            
            logger.info(f"✓ Loaded Whisper model: {model_size}")
            return model
            
        except Exception as e:
            logger.error(f"❌ Failed to load model {model_size}: {str(e)}")
            return None
    
    def transcribe_audio(self, audio_path: str, model_size: str = "base") -> Dict[str, Any]:
        """تحويل الصوت إلى نص"""
        try:
            model = self.load_model(model_size)
            if not model:
                return {"error": "Failed to load model"}
            
            # تنفيذ التحويل
            segments, info = model.transcribe(audio_path, beam_size=5)
            
            # تجميع النتائج
            text_segments = []
            full_text = ""
            
            for segment in segments:
                segment_data = {
                    "start": segment.start,
                    "end": segment.end,
                    "text": segment.text.strip()
                }
                text_segments.append(segment_data)
                full_text += segment.text + " "
            
            return {
                "success": True,
                "text": full_text.strip(),
                "segments": text_segments,
                "language": info.language,
                "language_probability": info.language_probability
            }
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {str(e)}")
            return {"error": str(e)}

class OllamaIntegration:
    """تكامل Ollama للترجمة النصية"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.available = False
        self._check_availability()
    
    def _check_availability(self):
        """فحص توفر خدمة Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                self.available = True
                logger.info("✓ Ollama service available")
            else:
                logger.warning("⚠ Ollama service not responding")
        except Exception as e:
            logger.warning(f"⚠ Ollama not accessible: {str(e)}")
    
    def translate_text(self, text: str, target_language: str = "Arabic", model: str = "llama3") -> Dict[str, Any]:
        """ترجمة النص باستخدام Ollama"""
        if not self.available:
            return {"error": "Ollama service not available"}
        
        try:
            prompt = f"""Translate the following English text to {target_language}. 
            Only return the translation, no additional text or explanation:

            {text}"""
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 2000
                }
            }
            
            response = requests.post(f"{self.base_url}/api/generate", 
                                   json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                translation = result.get('response', '').strip()
                
                return {
                    "success": True,
                    "translation": translation,
                    "model": model,
                    "source_language": "English",
                    "target_language": target_language
                }
            else:
                return {"error": f"Ollama API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"❌ Translation failed: {str(e)}")
            return {"error": str(e)}
    
    def get_available_models(self) -> List[str]:
        """الحصول على النماذج المتوفرة"""
        if not self.available:
            return []
        
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]
                return models
            return []
        except:
            return []

class PyTorchTextProcessor:
    """معالج النصوص باستخدام PyTorch"""
    
    def __init__(self):
        self.available = False
        self._check_availability()
    
    def _check_availability(self):
        """فحص توفر PyTorch"""
        try:
            import torch
            self.available = True
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(f"✓ PyTorch available on {self.device}")
        except ImportError:
            logger.warning("⚠ PyTorch not available")
    
    def create_embedding(self, text: str) -> Optional[List[float]]:
        """إنشاء embedding للنص باستخدام PyTorch"""
        if not self.available:
            return None
        
        try:
            import torch
            import torch.nn.functional as F
            
            # تحويل النص إلى tokens بسيط (يمكن تحسينه)
            tokens = [ord(c) for c in text.lower() if c.isalnum()]
            
            # إنشاء tensor
            tensor = torch.tensor(tokens, dtype=torch.float32)
            
            # تطبيق تحويل بسيط
            if len(tensor) > 0:
                # تقليل الأبعاد إلى 128
                if len(tensor) > 128:
                    tensor = tensor[:128]
                else:
                    # padding
                    padding = torch.zeros(128 - len(tensor))
                    tensor = torch.cat([tensor, padding])
                
                # normalization
                tensor = F.normalize(tensor, dim=0)
                return tensor.tolist()
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Embedding creation failed: {str(e)}")
            return None
    
    def similarity_score(self, text1: str, text2: str) -> float:
        """حساب درجة التشابه بين نصين"""
        if not self.available:
            return 0.0
        
        try:
            import torch
            import torch.nn.functional as F
            
            emb1 = self.create_embedding(text1)
            emb2 = self.create_embedding(text2)
            
            if emb1 and emb2:
                tensor1 = torch.tensor(emb1)
                tensor2 = torch.tensor(emb2)
                similarity = F.cosine_similarity(tensor1, tensor2, dim=0)
                return float(similarity)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"❌ Similarity calculation failed: {str(e)}")
            return 0.0

class FFmpegAudioProcessor:
    """معالج الصوت باستخدام FFmpeg"""
    
    def __init__(self):
        self.available = False
        self._check_availability()
    
    def _check_availability(self):
        """فحص توفر FFmpeg"""
        try:
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                self.available = True
                logger.info("✓ FFmpeg available")
            else:
                logger.warning("⚠ FFmpeg not working")
        except Exception as e:
            logger.warning(f"⚠ FFmpeg not available: {str(e)}")
    
    def extract_audio(self, video_path: str, output_path: str = None) -> Dict[str, Any]:
        """استخراج الصوت من الفيديو"""
        if not self.available:
            return {"error": "FFmpeg not available"}
        
        try:
            if not output_path:
                # إنشاء ملف مؤقت
                temp_dir = tempfile.gettempdir()
                output_path = os.path.join(temp_dir, f"audio_{os.getpid()}.wav")
            
            # أمر FFmpeg لاستخراج الصوت
            cmd = [
                'ffmpeg', '-i', video_path,
                '-vn',  # بدون فيديو
                '-acodec', 'pcm_s16le',  # كودك صوتي
                '-ar', '16000',  # معدل العينة
                '-ac', '1',  # قناة واحدة
                '-y',  # استبدال الملف الموجود
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 and os.path.exists(output_path):
                return {
                    "success": True,
                    "audio_path": output_path,
                    "duration": self._get_audio_duration(output_path)
                }
            else:
                return {"error": f"FFmpeg failed: {result.stderr}"}
                
        except Exception as e:
            logger.error(f"❌ Audio extraction failed: {str(e)}")
            return {"error": str(e)}
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """الحصول على مدة الملف الصوتي"""
        try:
            cmd = ['ffprobe', '-v', 'quiet', '-show_entries', 
                   'format=duration', '-of', 'csv=p=0', audio_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            return 0.0
            
        except:
            return 0.0

class AITranslationPipeline:
    """خط إنتاج الترجمة الذكية الكامل"""
    
    def __init__(self):
        self.whisper = FastWhisperIntegration()
        self.ollama = OllamaIntegration()
        self.pytorch = PyTorchTextProcessor()
        self.ffmpeg = FFmpegAudioProcessor()
        
        logger.info("🤖 AI Translation Pipeline initialized")
        self._log_status()
    
    def _log_status(self):
        """عرض حالة جميع المكونات"""
        components = {
            "Faster-Whisper": self.whisper.available,
            "Ollama": self.ollama.available,
            "PyTorch": self.pytorch.available,
            "FFmpeg": self.ffmpeg.available
        }
        
        for name, status in components.items():
            icon = "✓" if status else "✗"
            logger.info(f"{icon} {name}: {'Available' if status else 'Not Available'}")
    
    def process_video_file(self, video_path: str, output_srt_path: str = None) -> Dict[str, Any]:
        """معالجة ملف فيديو كاملة من الفيديو إلى ترجمة"""
        try:
            logger.info(f"🎬 Processing video: {video_path}")
            
            # 1. استخراج الصوت
            audio_result = self.ffmpeg.extract_audio(video_path)
            if "error" in audio_result:
                return audio_result
            
            audio_path = audio_result["audio_path"]
            logger.info(f"🎵 Audio extracted: {audio_path}")
            
            # 2. تحويل الصوت إلى نص
            transcription_result = self.whisper.transcribe_audio(audio_path)
            if "error" in transcription_result:
                return transcription_result
            
            logger.info(f"📝 Transcription completed")
            
            # 3. ترجمة النص
            translation_result = self.ollama.translate_text(
                transcription_result["text"], 
                target_language="Arabic"
            )
            
            if "error" in translation_result:
                return translation_result
            
            logger.info(f"🌍 Translation completed")
            
            # 4. إنشاء ملف SRT
            if not output_srt_path:
                video_name = Path(video_path).stem
                output_srt_path = f"{video_name}.ar.srt"
            
            srt_result = self._create_srt_file(
                transcription_result["segments"],
                translation_result["translation"],
                output_srt_path
            )
            
            # تنظيف الملف المؤقت
            try:
                os.unlink(audio_path)
            except:
                pass
            
            return {
                "success": True,
                "video_path": video_path,
                "srt_path": output_srt_path,
                "transcription": transcription_result["text"],
                "translation": translation_result["translation"],
                "language_detected": transcription_result.get("language", "en"),
                "segments_count": len(transcription_result["segments"])
            }
            
        except Exception as e:
            logger.error(f"❌ Video processing failed: {str(e)}")
            return {"error": str(e)}
    
    def _create_srt_file(self, segments: List[Dict], translation: str, output_path: str) -> Dict[str, Any]:
        """إنشاء ملف SRT"""
        try:
            # تقسيم الترجمة على أساس الفقرات
            translated_parts = translation.split('.')
            
            with open(output_path, 'w', encoding='utf-8') as srt_file:
                for i, segment in enumerate(segments):
                    if i < len(translated_parts):
                        translated_text = translated_parts[i].strip()
                    else:
                        translated_text = segment["text"]  # fallback
                    
                    if translated_text:
                        # تحويل الوقت إلى تنسيق SRT
                        start_time = self._seconds_to_srt_time(segment["start"])
                        end_time = self._seconds_to_srt_time(segment["end"])
                        
                        srt_file.write(f"{i + 1}\n")
                        srt_file.write(f"{start_time} --> {end_time}\n")
                        srt_file.write(f"{translated_text}\n\n")
            
            return {"success": True, "srt_path": output_path}
            
        except Exception as e:
            return {"error": f"SRT creation failed: {str(e)}"}
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """تحويل الثواني إلى تنسيق SRT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def get_system_status(self) -> Dict[str, Any]:
        """الحصول على حالة النظام"""
        return {
            "components": {
                "faster_whisper": self.whisper.available,
                "ollama": self.ollama.available,
                "pytorch": self.pytorch.available,
                "ffmpeg": self.ffmpeg.available
            },
            "ollama_models": self.ollama.get_available_models() if self.ollama.available else [],
            "system_ready": all([
                self.whisper.available,
                self.ollama.available,
                self.ffmpeg.available
            ])
        }

# إنشاء مثيل عام
ai_pipeline = AITranslationPipeline()

# دوال مساعدة للاستخدام المباشر
def process_video(video_path: str, output_srt: str = None) -> Dict[str, Any]:
    """معالجة فيديو كاملة"""
    return ai_pipeline.process_video_file(video_path, output_srt)

def transcribe_audio(audio_path: str, model_size: str = "base") -> Dict[str, Any]:
    """تحويل صوت إلى نص"""
    return ai_pipeline.whisper.transcribe_audio(audio_path, model_size)

def translate_text(text: str, target_lang: str = "Arabic") -> Dict[str, Any]:
    """ترجمة نص"""
    return ai_pipeline.ollama.translate_text(text, target_lang)

def extract_audio(video_path: str, output_path: str = None) -> Dict[str, Any]:
    """استخراج صوت من فيديو"""
    return ai_pipeline.ffmpeg.extract_audio(video_path, output_path)

def get_ai_status() -> Dict[str, Any]:
    """الحصول على حالة النظام"""
    return ai_pipeline.get_system_status()

if __name__ == "__main__":
    # اختبار المكونات
    status = get_ai_status()
    print("🤖 AI Translation Pipeline Status:")
    print(json.dumps(status, indent=2, ensure_ascii=False))