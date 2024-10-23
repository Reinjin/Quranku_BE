import os
import numpy as np
import librosa
from tensorflow.keras.models import load_model

# Daftar nama kelas
class_names = ['01. alif_fathah', '02. alif_kasroh', '03. alif_dommah', '04. ba_fathah', '05. ba_kasroh', '06. ba_dommah',
               '07. ta_fathah', '08. ta_kasroh', '09. ta_dommah', '10. tsa_fathah', '11. tsa_kasroh', '12. tsa_dommah',
               '13. jim_fathah', '14. jim_kasroh', '15. jim_dommah', '16. hah_fathah', '17. hah_kasroh', '18. hah_dommah',
               '19. kha_fathah', '20. kha_kasroh', '21. kha_dommah', '22. dal_fathah', '23. dal_kasroh', '24. dal_dommah',
               '25. dzal_fathah', '26. dzal_kasroh', '27. dzal_dommah', '28. ra_fathah', '29. ra_kasroh', '30. ra_dommah',
               '31. zay_fathah', '32. zay_kasroh', '33. zay_dommah', '34. sin_fathah', '35. sin_kasroh', '36. sin_dommah',
               '37. shin_fathah', '38. shin_kasroh', '39. shin_dommah', '40. sad_fathah', '41. sad_kasroh', '42. sad_dommah',
               '43. dad_fathah', '44. dad_kasroh', '45. dad_dommah', '46. tah_fathah', '47. tah_kasroh', '48. tah_dommah',
               '49. zah_fathah', '50. zah_kasroh', '51. zah_dommah', '52. ain_fathah', '53. ain_kasroh', '54. ain_dommah',
               '55. ghaiin_fathah', '56. ghaiin_kasroh', '57. ghaiin_dommah', '58. fa_fathah', '59. fa_kasroh', '60. fa_dommah',
               '61. qaf_fathah', '62. qaf_kasroh', '63. qaf_dommah', '64. kaf_fathah', '65. kaf_kasroh', '66. kaf_dommah',
               '67. lam_fathah', '68. lam_kasroh', '69. lam_dommah', '70. mim_fathah', '71. mim_kasroh', '72. mim_dommah',
               '73. nun_fathah', '74. nun_kasroh', '75. nun_dommah', '76. Ha_fathah', '77. Ha_kasroh', '78. Ha_dommah',
               '79. waw_fathah', '80. waw_kasroh', '81. waw_dommah', '82. ya_fathah', '83. ya_kasroh', '84. ya_dommah']

# Fungsi untuk memproses file audio (dari stream numpy array)
def load_and_preprocess_audio(y, sr, max_time_steps=128, n_mels=128, n_fft=2048, hop_length=512):
    # Ekstrak Mel Spectrogram
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=n_fft, hop_length=hop_length, n_mels=n_mels)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

    # Padding atau trimming spectrogram
    if mel_spec_db.shape[1] < max_time_steps:
        pad_width = max_time_steps - mel_spec_db.shape[1]
        mel_spec_db = np.pad(mel_spec_db, ((0, 0), (0, pad_width)), mode='constant')
    else:
        mel_spec_db = mel_spec_db[:, :max_time_steps]

    # Menambahkan dimensi tambahan untuk input ke CNN
    mel_spec_db = mel_spec_db[np.newaxis, ..., np.newaxis]
    
    return mel_spec_db

# Fungsi prediksi
def predict_audio_class(y, sr, model_path='model.keras'):
    # Ubah path relatif menjadi path absolut
    current_directory = os.path.dirname(os.path.abspath(__file__))
    model_file_path = os.path.join(current_directory, model_path)

    # Muat model
    if not os.path.exists(model_file_path):
        raise FileNotFoundError(f"File not found: {model_file_path}. Please ensure the file is an accessible `.keras` zip file.")
    
    model = load_model(model_file_path)

    # Preprocessing audio
    processed_audio = load_and_preprocess_audio(y, sr)

    # Lakukan prediksi
    predictions = model.predict(processed_audio)
    
    predicted_class_index = np.argmax(predictions, axis=-1)[0]
    
    predicted_class_name = class_names[predicted_class_index]
    
    return predicted_class_name