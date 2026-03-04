import streamlit as st
import speech_recognition as sr

# Optimisation : On garde l'instance du recognizer en cache
@st.cache_resource
def get_recognizer():
    return sr.Recognizer()

def transcribe_speech(api_choice, language_code):
    r = get_recognizer()
    
    try:
        with sr.Microphone() as source:
            status = st.empty() # Espace dynamique pour les messages d'état
            
            status.info("⏳ Réglage du bruit ambiant...")
            r.adjust_for_ambient_noise(source, duration=0.8)
            
            status.warning("🎤 Parlez maintenant...")
            audio_text = r.listen(source, timeout=5, phrase_time_limit=12)
            
            status.info("🤖 Transcription en cours...")
            
            if api_choice == "Google":
                text = r.recognize_google(audio_text, language=language_code)
            else:
                text = r.recognize_sphinx(audio_text, language=language_code)
            
            status.empty() # Nettoie le dernier message
            return text

    except sr.WaitTimeoutError:
        return "❌ Erreur : Aucun son détecté."
    except sr.UnknownValueError:
        return "❌ Erreur : L'audio n'a pas été compris."
    except sr.RequestError:
        return "❌ Erreur : Problème de connexion au service."
    except OSError:
        return "❌ Erreur : Aucun microphone détecté sur ce système."
    except Exception as e:
        return f"❌ Erreur imprévue : {e}"

def main():
    st.set_page_config(page_title="Voice Assistant", page_icon="🎙️")
    st.title("🎙️ Assistant de Reconnaissance Vocale")

    # --- Sidebar ---
    with st.sidebar:
        st.header("⚙️ Configuration")
        api_choice = st.selectbox("API", ["Google", "Sphinx (Hors-ligne)"])
        lang_choice = st.selectbox("Langue", ["fr-FR", "en-US", "es-ES", "de-DE"])
        st.divider()
        st.caption("Note: Google nécessite une connexion internet.")

    # --- Gestion de l'état ---
    if "is_paused" not in st.session_state:
        st.session_state.is_paused = False
    if "transcript" not in st.session_state:
        st.session_state.transcript = ""

    # --- Contrôles ---
    col1, col2 = st.columns([1, 4])
    
    with col1:
        btn_label = "▶️ Reprendre" if st.session_state.is_paused else "⏸️ Pause"
        if st.button(btn_label):
            st.session_state.is_paused = not st.session_state.is_paused
            st.rerun()

    if st.session_state.is_paused:
        st.warning("Système en pause.")
    else:
        if st.button("🎤 Lancer l'enregistrement", type="primary", use_container_width=True):
            result = transcribe_speech(api_choice, lang_choice)
            
            if "❌" in result:
                st.error(result)
            else:
                st.session_state.transcript = result
                st.success("Transcription réussie !")

    # --- Affichage du résultat ---
    if st.session_state.transcript:
        with st.expander("📄 Résultat de la transcription", expanded=True):
            new_text = st.text_area("Modifier le texte si nécessaire :", 
                                    value=st.session_state.transcript, 
                                    height=200)
            
            st.download_button(
                label="💾 Télécharger en .txt",
                data=new_text,
                file_name="transcription.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
