import './physgpt.css';
import { useState } from 'react';

import { faPaperPlane, faSpinner } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import { Overlay, Modal } from '../components/Modal'

const PhysGPT = () => {
    const [modalOpen, setModalOpen] = useState(false);
    const [loading, setLoading] = useState(false);

    const searchHandler = () => {
        setLoading(true);
        setTimeout(() => alert('I wish it worked too.'), 0);
        setTimeout(() => setLoading(false), 3000);
    };

    return (
        // This page should validate the user and redirect if unauthenticated.
        <div className={`app-container${loading ? ' loading': ''}`}>
            {
                modalOpen ? (
                    <Overlay close={() => setModalOpen(false)}>
                        <Modal title="References" close={() => setModalOpen(false)}>Test</Modal>
                    </Overlay>
                ) : null
            }
            <div className="chat-container">
                <div className="chat-background">
                    <section className="user-query">
                        <p>Ask a question below.</p>
                    </section>
                    <section className="gpt-reply">
                        <p>Congratulations, you have exclusive access to the worlds most knowledgable physicist, what would you like to know?</p>
                        <div>
                            {/* div wrapper is needed so flex doesn't stretch click area */}
                            <div className="link" onClick={() => setModalOpen(true)}>References</div>
                        </div>
                    </section>

                    <section className="user-query">
                        <p>Ask a question below.</p>
                    </section>
                    <section className="gpt-reply">
                        <p>Congratulations, you have exclusive access to the worlds most knowledgable physicist, what would you like to know?</p>
                    </section>
                    <section className="user-query">
                        <p>Ask a question below.</p>
                    </section>
                    <section className="gpt-reply">
                        <p>Congratulations, you have exclusive access to the worlds most knowledgable physicist, what would you like to know?</p>
                    </section>
                    <section className="user-query">
                        <p>Ask a question below.</p>
                    </section>
                    <section className="gpt-reply">
                        <p>Congratulations, you have exclusive access to the worlds most knowledgable physicist, what would you like to know?</p>
                    </section>
                    <section className="user-query">
                        <p>Ask a question below.</p>
                    </section>
                    <section className="gpt-reply">
                        <p>Congratulations, you have exclusive access to the worlds most knowledgable physicist, what would you like to know?</p>
                    </section>
                    <section className="user-query">
                        <p>Ask a question below.</p>
                    </section>
                    <section className="gpt-reply">
                        <p>Congratulations, you have exclusive access to the worlds most knowledgable physicist, what would you like to know?</p>
                    </section>
                    <div className="chat-fader"></div>
                </div>
            </div>
            <div className="input-container">
                <label htmlFor="search">Ask her a question</label>
                <textarea id="search" className={`user-input${loading ? ' disabled' : ''}`}></textarea>
                <div className={`query-icon${loading ? ' disabled' : ''}`}>
                    <FontAwesomeIcon
                        className={loading ? 'disabled' : ''}
                        onClick={searchHandler}
                        spin={loading}
                        icon={loading ? faSpinner : faPaperPlane}
                        title="Send"
                    />
                </div>
            </div>
        </div>
    );
}

export default PhysGPT
