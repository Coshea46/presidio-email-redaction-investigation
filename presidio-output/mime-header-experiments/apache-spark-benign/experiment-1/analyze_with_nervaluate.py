import csv
import json
import sys
from nervaluate import Evaluator
import yaml


def resolve_ground_truths_and_ids(ground_truth_csv_path):

    email_dictionary_list = []

    with open(ground_truth_csv_path, mode='r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f) 
        next(reader, None)

        for row in reader:
            email_id = row[1]

            corresponding_email_dict = next((d for d in email_dictionary_list if d.get("email_id") == email_id), None)
            
            if corresponding_email_dict is None:
                new_email_dict = {
                    "email_id": email_id,
                    "gold_spans": [],
                    "pred_spans": []
                }
                corresponding_email_dict = new_email_dict
                email_dictionary_list.append(corresponding_email_dict)

            start_index_of_span = int(row[3])
            end_index_of_span = int(row[4])
            entity_type = row[5]

            # CUSTOM LOGIC: these are fine-grained ground truth subtypes that
            # should be merged into their broader category for this experiment,
            # since Presidio's taxonomy doesn't distinguish them
            if entity_type == "DOMAIN":
                entity_type = "URL"

            if entity_type == "MESSAGE_ID":
                entity_type = "EMAIL_ADDRESS"

            corresponding_email_dict["gold_spans"].append((start_index_of_span, end_index_of_span, entity_type))

    return email_dictionary_list


def resolve_predicted_spans(predicted_spans_csv_path, email_dictionary_list):

    with open(predicted_spans_csv_path, mode='r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f) 
        next(reader, None)

        for row in reader:
            email_id = row[1]
            corresponding_email_dict = next((d for d in email_dictionary_list if d.get("email_id") == email_id), None)

            start_index_of_span = int(row[3])
            end_index_of_span = int(row[4])
            entity_type = row[5]

            corresponding_email_dict["pred_spans"].append((start_index_of_span, end_index_of_span, entity_type))
             


def resolve_email_text(label_studio_tasks_json_path, email_dictionary_list):
    with open(label_studio_tasks_json_path, mode='r') as f:
        tasks_json_content_list = json.load(f)

        for email_entry in tasks_json_content_list:
            current_email_id = email_entry["data"]["email_id"]
            current_email_as_text = email_entry["data"]["text"]
            
            # Find the dict
            corresponding_email_dict = next((d for d in email_dictionary_list if d.get("email_id") == current_email_id), None)
            
            if corresponding_email_dict:
                corresponding_email_dict["text"] = current_email_as_text
                
 
def compute_nervaluate_stats(email_dictionary_list, taxonomy_yaml_path):

    with open(taxonomy_yaml_path, mode='r',encoding='utf-8') as f:
        taxonomy_dict = yaml.safe_load(f)

        labels_in_taxonomy = taxonomy_dict["entities"]["en"]

    
    ground_truths_master = []
    predictions_master = []

    for email_dict in email_dictionary_list:

        # build up ground truth lables list for current email dict
        current_email_ground_truths = []
        current_email_predictions = []

        for ground_truth in email_dict["gold_spans"]:

            label_as_dict = {}

            start, end, label = ground_truth

            label_as_dict["label"] = label
            label_as_dict["start"] = start
            label_as_dict["end"] = end 

            current_email_ground_truths.append(label_as_dict)
        

        for prediction in email_dict["pred_spans"]:

            label_as_dict = {}

            start, end, label = prediction

            label_as_dict["label"] = label
            label_as_dict["start"] = start
            label_as_dict["end"] = end 

            current_email_predictions.append(label_as_dict)
        

        ground_truths_master.append(current_email_ground_truths)
        predictions_master.append(current_email_predictions)

    evaluator = Evaluator(ground_truths_master, predictions_master, tags=list(labels_in_taxonomy))

    evaluation_output = evaluator.evaluate()

    results = evaluation_output['overall']
    results_by_tag = evaluation_output['entities']
    
    return results, results_by_tag, labels_in_taxonomy


def display_nervaluate_results(results_by_tag, labels_in_taxonomy):
    # Added True Positives (Correct), False Positives (Spurious), and False Negatives (Missed)
    print("| Entity Type | Evaluation Schema | Correct (TP) | False Pos (Spurious) | Missed (FN) | Precision | Recall | F1-Score |")
    print("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    
    for tag in sorted(labels_in_taxonomy):
        tag_metrics = results_by_tag.get(tag)
        
        if not tag_metrics:
            strict_c = strict_fp = strict_fn = strict_p = strict_r = strict_f1 = "N/A"
            exact_c = exact_fp = exact_fn = exact_p = exact_r = exact_f1 = "N/A"
            partial_c = partial_fp = partial_fn = partial_p = partial_r = partial_f1 = "N/A"
            type_c = type_fp = type_fn = type_p = type_r = type_f1 = "N/A"
        else:
            # 1. Strict (Exact Boundary + Exact Type)
            strict_c = tag_metrics['strict'].correct
            strict_fp = tag_metrics['strict'].spurious
            strict_fn = tag_metrics['strict'].missed
            strict_p = f"{tag_metrics['strict'].precision:.2f}"
            strict_r = f"{tag_metrics['strict'].recall:.2f}"
            strict_f1 = f"{tag_metrics['strict'].f1:.2f}"
            
            # 2. Exact (Exact Boundary, Any Type)
            exact_c = tag_metrics['exact'].correct
            exact_fp = tag_metrics['exact'].spurious
            exact_fn = tag_metrics['exact'].missed
            exact_p = f"{tag_metrics['exact'].precision:.2f}"
            exact_r = f"{tag_metrics['exact'].recall:.2f}"
            exact_f1 = f"{tag_metrics['exact'].f1:.2f}"
            
            # 3. Partial (Overlapping Boundary, Any Type)
            partial_c = tag_metrics['partial'].correct
            partial_fp = tag_metrics['partial'].spurious
            partial_fn = tag_metrics['partial'].missed
            partial_p = f"{tag_metrics['partial'].precision:.2f}"
            partial_r = f"{tag_metrics['partial'].recall:.2f}"
            partial_f1 = f"{tag_metrics['partial'].f1:.2f}"
            
            # 4. Ent_type (Overlapping Boundary + Exact Type)
            type_c = tag_metrics['ent_type'].correct
            type_fp = tag_metrics['ent_type'].spurious
            type_fn = tag_metrics['ent_type'].missed
            type_p = f"{tag_metrics['ent_type'].precision:.2f}"
            type_r = f"{tag_metrics['ent_type'].recall:.2f}"
            type_f1 = f"{tag_metrics['ent_type'].f1:.2f}"
        
        print(f"| **{tag}** | Strict (Exact Type + Span) | {strict_c} | {strict_fp} | {strict_fn} | {strict_p} | {strict_r} | {strict_f1} |")
        print(f"| **{tag}** | Exact (Span Boundaries Only) | {exact_c} | {exact_fp} | {exact_fn} | {exact_p} | {exact_r} | {exact_f1} |")
        print(f"| **{tag}** | Partial (Overlapping Span Only) | {partial_c} | {partial_fp} | {partial_fn} | {partial_p} | {partial_r} | {partial_f1} |")
        print(f"| **{tag}** | Type (Overlapping Span + Exact Type) | {type_c} | {type_fp} | {type_fn} | {type_p} | {type_r} | {type_f1} |")
        print("| --- | --- | --- | --- | --- | --- | --- | --- |")



def save_mismatches_to_csv(email_dictionary_list, output_csv="mismatches.csv", fp_output_csv="spurious_false_positives.csv"):
    with open(output_csv, 'w', newline='', encoding='utf-8') as f, \
         open(fp_output_csv, 'w', newline='', encoding='utf-8') as fp_f:

        writer = csv.writer(f)
        writer.writerow(["email_id", "tag", "type", "start", "end", "text"])

        fp_writer = csv.writer(fp_f)
        fp_writer.writerow(["email_id", "tag", "start", "end", "text"])

        for email_dict in email_dictionary_list:
            email_text = email_dict.get("text", "")

            # Check for False Negatives (Missed by Presidio)
            # Now requires start, end, AND type to match for a "hit"
            for gold in email_dict["gold_spans"]:
                if not any(gold[0] == pred[0] and gold[1] == pred[1] and gold[2] == pred[2]
                           for pred in email_dict["pred_spans"]):
                    missed_text = email_text[gold[0]:gold[1]] if email_text else "N/A"
                    writer.writerow([email_dict["email_id"], gold[2], "MISSED_BY_PRESIDIO", gold[0], gold[1], missed_text])

            # Check for False Positives (Extra things Presidio found)
            # Now requires start, end, AND type to match for a "hit"
            for pred in email_dict["pred_spans"]:
                if not any(pred[0] == gold[0] and pred[1] == gold[1] and pred[2] == gold[2]
                           for gold in email_dict["gold_spans"]):
                    spurious_text = email_text[pred[0]:pred[1]] if email_text else "N/A"
                    writer.writerow([email_dict["email_id"], pred[2], "EXTRA_PRESIDIO_PRED", pred[0], pred[1], spurious_text])
                    fp_writer.writerow([email_dict["email_id"], pred[2], pred[0], pred[1], spurious_text])

    print(f"Mismatch report saved to {output_csv}")
    print(f"Spurious false positives report saved to {fp_output_csv}")


def main(args):

    # args should be in order: ground truth csv path, predicted spans csv path, label studio tasks json path, taxonomy yaml path
    ground_truth_csv_path = args[0]
    predicted_spans_csv_path = args[1]
    label_studio_task_json_path = args[2]
    taxonomy_yaml_path = args[3]

    emails_as_dictionaries_list = resolve_ground_truths_and_ids(ground_truth_csv_path)
    resolve_predicted_spans(predicted_spans_csv_path, emails_as_dictionaries_list)
    resolve_email_text(label_studio_task_json_path, emails_as_dictionaries_list)

    save_mismatches_to_csv(emails_as_dictionaries_list)

    nervaluate_results, nervaluate_results_by_tag, labels_in_taxonomy = compute_nervaluate_stats(emails_as_dictionaries_list, taxonomy_yaml_path)

    display_nervaluate_results(nervaluate_results_by_tag, labels_in_taxonomy)




if __name__ == "__main__":
    
    main(sys.argv[1:])
