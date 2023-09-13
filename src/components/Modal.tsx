import { MouseEventHandler } from 'react';
import { Props } from '../types/types';

interface OverlayProps extends Props {
    close?: Function
};

export const Overlay = (props: OverlayProps) => {
    const overlayClickHandler: MouseEventHandler = (event) => {
        event.preventDefault();
        event.stopPropagation();
        props.close();
    }
    return <div onClick={overlayClickHandler} className="overlay">{props.children}</div>
};

interface ModalProps extends Props {
    title?: string,
    close: Function
};

export const Modal = (props: ModalProps) => {
    const modalClickHandler: MouseEventHandler = (event) => {
        event.preventDefault();
        event.stopPropagation();
        props.close();
    }
    return (
        <div className="modal" onClick={(event) => {event.stopPropagation()}}>
            <h1>{props.title}</h1>
            {props.children}
            <div className="button-tray">
                <button onClick={modalClickHandler}>Close</button>
            </div>
        </div>
    )
};
