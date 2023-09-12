import { faPaperPlane } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

const PhysGPT = () => {
    return (
        // This page should validate the user and redirect if unauthenticated.
        <div className="app-container">
            <div className="chat-container">
                <div className="chat-background">
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
                    <section className="user-query">
                        <p>Ask a question below.</p>
                    </section>
                    <section className="gpt-reply">
                        <p>Congratulations, you have exclusive access to the worlds most knowledgable physicist, what would you like to know?</p>
                    </section>
                </div>
            </div>
            <div className="input-container">
                <label htmlFor="search">Ask it any question</label>
                <textarea id="search" className="user-input"></textarea>
                <FontAwesomeIcon className="query-icon" onClick={() => {alert('I wish it worked too.')}} icon={faPaperPlane} title="Send" />
            </div>
        </div>
    );
}

export default PhysGPT
