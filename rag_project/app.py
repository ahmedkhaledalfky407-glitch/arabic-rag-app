# -*- coding: utf-8 -*-
"""
نقطة الدخول الرئيسية - تشغيل الخادم الخلفي والواجهة الأمامية.
"""

import os
import sys
import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"🚀 Starting server on http://0.0.0.0:{port}")
    uvicorn.run("server:app", host="0.0.0.0", port=port, log_level="info")
