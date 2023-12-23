#! /usr/bin/env python
# -*- coding: utf-8 -*-

import json
import lzma
import os
import os.path as osp
import pickle
import shutil

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.markers import MarkerStyle


class Audiogram:
    def __init__(self, pkl_path: str, cache_dir="cache") -> None:
        """Initialize an instance of the Audiogram class.

        Args:
            pkl_path (str): The path to the pickle file containing the audiogram data.
            cache_dir (str, optional): The directory to store cached patient information and plots. Defaults to "cache".
        """
        self.pkl_path = pkl_path
        self.patient_info_dir = osp.join(cache_dir, "patient_info")
        self.plots_dir = osp.join(cache_dir, "plots")
        self.data = self.load_pkl(pkl_path)
        self.n_sample = len(self.data["age"])

    def load_pkl(self, pkl_path: str) -> dict:
        """Load a pickled object from the specified path.

        Args:
            pkl_path (str): The path to the pickled object.

        Returns:
            object: The unpickled object.
        """
        with lzma.open(pkl_path, "rb") as f:
            return pickle.load(f)

    def load_json(self, path: str) -> dict:
        """Load a JSON file and return its contents as a dictionary.

        Args:
            path (str): The path to the JSON file.

        Returns:
            dict: The contents of the JSON file as a dictionary.
        """
        with open(path) as f:
            return json.load(f)

    def save_json(self, path: str, data: dict) -> None:
        """Save a dictionary as JSON to a file.

        Args:
            path (str): The path to the file where the JSON data will be saved.
            data (dict): The dictionary to be saved as JSON.
        """
        with open(path, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _cache_patient_info(self, idx: int, fpath: str) -> None:
        """Cache patient information.

        Args:
            idx (int): The index of the patient.
            fpath (str): The file path to save the cached data.
        """
        if osp.exists(fpath):
            return
        os.makedirs(self.patient_info_dir, exist_ok=True)
        save_data = {
            "Patient-ID": idx,
            "Sex": self.data["sex"][idx],
            "Age": self.data["age"][idx],
            "AC (R)": ", ".join([str(x) for x in self.data["gram_info"][idx]["acr"]]),
            "AC (L)": ", ".join([str(x) for x in self.data["gram_info"][idx]["acl"]]),
            "BC (R)": ", ".join([str(x) for x in self.data["gram_info"][idx]["bcr"]]),
            "BC (L)": ", ".join([str(x) for x in self.data["gram_info"][idx]["bcl"]]),
            "PTA (R)": f"{np.mean(self.data['gram_info'][idx]['acr'][1:5]):.1f}",
            "PTA (L)": f"{np.mean(self.data['gram_info'][idx]['acl'][1:5]):.1f}",
        }
        self.save_json(fpath, save_data)

    def _cache_plot(self, idx: int, earside: str, fpath: str) -> None:
        """Caches the plot for a given index, earside, and file path.

        Args:
            idx (int): The index of the patient.
            earside (str): The earside for which the plot is generated.
            fpath (str): The file path where the plot will be saved.
        """
        if osp.exists(fpath):
            return
        os.makedirs(self.plots_dir, exist_ok=True)
        gram_info = self.data["gram_info"][idx]
        assert earside in {"l", "r"}
        self.save_plot(gram_info, earside=earside, save_path=fpath)

    def cache_all(self) -> None:
        """Caches patient information and plots for all samples.

        This method iterates over all samples and caches the patient information
        as well as the plots for both the left and right ears.
        """
        for i in range(self.n_sample):
            print(f"caching {i}/{self.n_sample}")
            self._cache_patient_info(i, fpath=osp.join(self.patient_info_dir, f"{i}.json"))
            self._cache_plot(i, earside="l", fpath=osp.join(self.plots_dir, f"{i}-left.png"))
            self._cache_plot(i, earside="r", fpath=osp.join(self.plots_dir, f"{i}-right.png"))

    def patient_info(self, idx: int) -> dict:
        """Retrieve the patient information for a given index.

        Args:
            idx (int): The index of the patient.

        Returns:
            dict: The patient information as a dictionary.
        """
        fpath = osp.join(self.patient_info_dir, f"{idx}.json")
        if not osp.isfile(fpath):
            self._cache_patient_info(idx, fpath)
        return self.load_json(fpath)

    def plots(self, idx: int) -> dict:
        """Generate and cache plots for the given index.

        Args:
            idx (int): The index of the patient.

        Returns:
            dict: A dictionary containing the file paths of the generated plots.
                  The keys are 'left' and 'right', corresponding to the left and right plots, respectively.
        """
        left = osp.join(self.plots_dir, f"{idx}-left.png")
        right = osp.join(self.plots_dir, f"{idx}-right.png")
        if not osp.isfile(left):
            self._cache_plot(idx, "l", left)
        if not osp.isfile(right):
            self._cache_plot(idx, "r", right)
        return {"left": left, "right": right}

    def save_plot(self, info: dict, earside: str, save_path: str) -> None:
        """Save audiogram plot for a given patient.

        Args:
            info (dict): patient information.
            earside (str): ear side. "l" for left, "r" for right.
            save_path (str): file path to save the plot.
        """
        assert earside in {"l", "r"}
        freqs = ["250", "500", "1K", "2K", "4K", "8K"]
        fig, ax = plt.subplots(dpi=300, figsize=(5, 6))
        xticks = np.arange(len(freqs))
        ax.set_xlabel("Freq / Hz", loc="right")
        ax.set_ylabel("Intensity / dBHL")
        ax.set_xlim(-0.5, xticks[-1] + 0.5)
        ax.set_ylim(-20, 125)
        ax.xaxis.tick_top()
        ax.xaxis.set_label_position("top")
        plt.setp(ax, xticks=xticks, xticklabels=freqs)
        major_ticks = np.arange(-20, 120, 10)
        minor_ticks = np.arange(-20, 120, 5)
        ax.set_yticks(major_ticks)
        ax.set_yticks(minor_ticks, minor=True)
        ax.set_axisbelow(b=True)
        ax.grid(color="gray", linestyle="dashed")
        ax.invert_yaxis()
        ax.tick_params(axis="x", labelsize=6.5)
        ax.tick_params(axis="y", labelsize=6.5)
        ax.set_title(f"{'Left' if earside == 'l' else 'Right'} Audiogram")

        colors = {"l": "b", "r": "r"}
        markers = {
            "acl_masked_resp": "s",
            "acl_masked_noresp": "D",
            "acl_unmasked_resp": "x",
            "acl_unmasked_noresp": "+",
            "bcl_masked_resp": "$]$",
            "bcl_masked_noresp": "$]-$",
            "bcl_unmasked_resp": 5,
            "bcl_unmasked_noresp": "4",
            "acr_masked_resp": "^",
            "acr_masked_noresp": "*",
            "acr_unmasked_resp": "o",
            "acr_unmasked_noresp": "8",
            "bcr_masked_resp": "$[$",
            "bcr_masked_noresp": "$-[$",
            "bcr_unmasked_resp": 4,
            "bcr_unmasked_noresp": "3",
        }
        color = colors[earside]

        # Air condution
        ax.plot(info[f"ac{earside}"], color=color, linestyle="-", linewidth=1)

        masked_resp_x = []
        masked_resp_y = []

        masked_noresp_x = []
        masked_noresp_y = []

        unmasked_resp_x = []
        unmasked_resp_y = []

        unmasked_noresp_x = []
        unmasked_noresp_y = []

        for idx in range(len(freqs)):
            if info[f"ac{earside}_noresp"][idx]:  # NoResp
                if info[f"ac{earside}_masked"][idx]:  # NoResp + Masking
                    masked_noresp_x.append(idx)
                    masked_noresp_y.append(info[f"ac{earside}"][idx])
                else:  # NoResp + NoMasking
                    unmasked_noresp_x.append(idx)
                    unmasked_noresp_y.append(info[f"ac{earside}"][idx])
            elif info[f"ac{earside}_masked"][idx]:  # Resp + Masking
                masked_resp_x.append(idx)
                masked_resp_y.append(info[f"ac{earside}"][idx])
            else:  # Resp + NoMasking
                unmasked_resp_x.append(idx)
                unmasked_resp_y.append(info[f"ac{earside}"][idx])

        if masked_resp_x:
            ax.scatter(
                masked_resp_x,
                masked_resp_y,
                s=200,
                c=color,
                marker=MarkerStyle(markers[f"ac{earside}_masked_resp"], fillstyle="none"),
                label="AC masked",
            )

        if masked_noresp_x:
            ax.scatter(
                masked_noresp_x,
                masked_noresp_y,
                s=200,
                c="k",
                marker=MarkerStyle(markers[f"ac{earside}_masked_noresp"], fillstyle="none"),
                label="AC masked NoResp",
            )

        if unmasked_resp_x:
            ax.scatter(
                unmasked_resp_x,
                unmasked_resp_y,
                s=200,
                c=color,
                marker=MarkerStyle(markers[f"ac{earside}_unmasked_resp"], fillstyle="none"),
                label="AC",
            )

        if unmasked_noresp_x:
            ax.scatter(
                unmasked_noresp_x,
                unmasked_noresp_y,
                s=200,
                c="k",
                marker=MarkerStyle(markers[f"ac{earside}_unmasked_noresp"], fillstyle="none"),
                label="AC NoResp",
            )

        # Bone conduction
        ax.plot(info[f"bc{earside}"], color=color, linestyle=":", linewidth=1.5)

        masked_resp_x = []
        masked_resp_y = []

        masked_noresp_x = []
        masked_noresp_y = []

        unmasked_resp_x = []
        unmasked_resp_y = []

        unmasked_noresp_x = []
        unmasked_noresp_y = []

        for idx in range(len(freqs) - 1):
            if info[f"bc{earside}_noresp"][idx]:  # NoResp
                if info[f"bc{earside}_masked"][idx]:  # NoResp + Masking
                    masked_noresp_x.append(idx)
                    masked_noresp_y.append(info[f"bc{earside}"][idx])
                else:  # NoResp + NoMasking
                    unmasked_noresp_x.append(idx)
                    unmasked_noresp_y.append(info[f"bc{earside}"][idx])
            elif info[f"bc{earside}_masked"][idx]:  # Resp + Masking
                masked_resp_x.append(idx)
                masked_resp_y.append(info[f"bc{earside}"][idx])
            else:  # Resp + NoMasking
                unmasked_resp_x.append(idx)
                unmasked_resp_y.append(info[f"bc{earside}"][idx])

        if masked_resp_x:
            ax.scatter(
                masked_resp_x,
                masked_resp_y,
                s=200,
                c=color,
                marker=MarkerStyle(markers[f"bc{earside}_masked_resp"], fillstyle="none"),
                label="BC masked",
            )

        if masked_noresp_x:
            ax.scatter(
                masked_noresp_x,
                masked_noresp_y,
                s=200,
                c="k",
                marker=MarkerStyle(markers[f"bc{earside}_masked_noresp"], fillstyle="none"),
                label="BC masked NoResp",
            )

        if unmasked_resp_x:
            ax.scatter(
                unmasked_resp_x,
                unmasked_resp_y,
                s=200,
                c=color,
                marker=MarkerStyle(markers[f"bc{earside}_unmasked_resp"], fillstyle="none"),
                label="BC",
            )

        if unmasked_noresp_x:
            ax.scatter(
                unmasked_noresp_x,
                unmasked_noresp_y,
                s=200,
                c="k",
                marker=MarkerStyle(markers[f"bc{earside}_unmasked_noresp"], fillstyle="none"),
                label="BC NoResp",
            )

        # Shrink current axis's height by 10% on the bottom
        box = ax.get_position()
        ax.set_position([box.x0, box.y0 + box.height * 0.1, box.width, box.height * 0.9])

        ax.legend(bbox_to_anchor=(0, -0.16), ncol=2, loc="lower left")
        fig.savefig(save_path)
        plt.close()


if __name__ == "__main__":
    shutil.rmtree("cache", ignore_errors=True)
    audiogram = Audiogram("anonymized-data.pkl.xz")
    audiogram.cache_all()
