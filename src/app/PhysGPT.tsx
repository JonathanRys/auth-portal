import './physgpt.css';
import { MouseEventHandler, useState } from 'react';

import { faPaperPlane } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

import { Props } from '../types/types';

interface OverlayProps extends Props {
    close?: MouseEventHandler
};
const Overlay = (props: OverlayProps) => {
    return <div onClick={props.close} className="overlay">{props.children}</div>
};

interface ModalProps extends Props {
    title?: string,
    close: MouseEventHandler
};
const Modal = (props: ModalProps) => {
    return (
        <div className="modal" onClick={(event) => {event.stopPropagation()}}>
            <h1>{props.title}</h1>
            {props.children}
            <div className="button-tray">
                <button onClick={props.close}>Close</button>
            </div>
        </div>
    )
};

const PhysGPT = () => {
    const [modalOpen, setModalOpen] = useState(false);

    const overlayHandler: MouseEventHandler = (event) => {
        event.preventDefault();
        event.stopPropagation();
        setModalOpen(false);
    }

    return (
        // This page should validate the user and redirect if unauthenticated.
        <div className="app-container">
            {
                modalOpen ? (
                    <Overlay close={overlayHandler}>
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
                        <div className="link" onClick={() => setModalOpen(true)}>References</div>
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
                <label htmlFor="search">Ask her a question</label>
                <textarea id="search" className="user-input"></textarea>
                <FontAwesomeIcon className="query-icon" onClick={() => {alert('I wish it worked too.')}} icon={faPaperPlane} title="Send" />
            </div>
        </div>
    );
}

export default PhysGPT
