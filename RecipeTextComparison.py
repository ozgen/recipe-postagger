from __future__ import division

import os

import utils

import UtilsIO

PRED = "PRED"  # verb tag
PRED_PREP = "PRED_PREP"  # verb tag with adp
DOBJ = "DOBJ"  # obj that is not related with ingredient
NON_INGREDIENT_SPAN = "NON_INGREDIENT_SPAN"  # obj that is not related with ingredient
NON_INGREDIENT_SPAN_VERB = "NON_INGREDIENT_SPAN_VERB"  # obj that is not related with ingredient
INGREDIENT_SPAN = "INGREDIENT_SPAN"  # obj that is related with ingredient
INGREDIENTS = "INGREDIENTS"  # pure ingredient
PARG = "PARG"  # tool
PREP = "PREP"  # preposition
PREDID = "PREDID"  # this id is realed with action's order

TAGGED_ARRAY = [PRED, PRED_PREP, NON_INGREDIENT_SPAN_VERB, INGREDIENT_SPAN, INGREDIENTS,
                PARG]

RESULTS_URL = "/Users/Ozgen/Desktop/RecipeGit/results/"+utils.TEXT_FOLDER_NAME
ANNOTATED_URL = "/Users/Ozgen/Desktop/RecipeGit/results/AnnotationSession-args"

RESULTS_URL2 = "/Users/Ozgen/Desktop/RecipeGit/results/paper_general_data/ChickenSalad/ChickenSalad-chunked"
RESULTS_URL3 = "/Users/Ozgen/Desktop/RecipeGit/results/paper_general_data/ChickenSalad/our_model_result"
ANNOTATED_URL2 = "/Users/Ozgen/Desktop/RecipeGit/results/paper_general_data/ChickenSalad/ChickenSalad-args"


def compareTwoSameSentence(sentenceResult, sentenceTaggedData):
    tmp_res = []

    for specific_tag in TAGGED_ARRAY:
        # we calculate percentages  for compare tagged and results
        a = compareTwoSameSentenceSpecificTag(sentenceResult, sentenceTaggedData, specific_tag)
        if a != None:
            tmp_res.append(a)

    if len(tmp_res) > 0:
        cnt_t = 0
        tot = 0
        for b in list(tmp_res):
            (cnt, total) = b
            cnt_t = cnt_t + int(cnt)
            tot = tot + int(total)

        result = float(cnt_t / tot)
        return result
    else:
        return None


def compareTwoSameSentenceSpecificTag(sentenceResult, sentenceTaggedData, specific_tag):
    result = [word for (word, tag, idx) in sentenceResult if tag == specific_tag]
    taggedData = [word for (word, tag, idx) in sentenceTaggedData if tag == specific_tag]

    if specific_tag == PARG:
        tmp = [word for (word, tag, idx) in sentenceResult if tag == NON_INGREDIENT_SPAN_VERB]
        result.extend(tmp)
    elif specific_tag == INGREDIENTS:
        tmp = [word for (word, tag, idx) in sentenceResult if tag == INGREDIENT_SPAN]
        result.extend(tmp)

    return compareTwoArray(taggedA=taggedData, resultA=result)


def compareTwoArray(taggedA, resultA):
    cnt = 0
    if len(taggedA) == 0:
        return None
    for word in resultA:
        for taggedWord in taggedA:
            # todo bug is here ...
            if compareTwoWords(word_res=word, word_tag=taggedWord):
                cnt = cnt + 1
    return (cnt, len(taggedA))  # float(cnt / len(taggedA))


def compareTwoWords(word_res, word_tag):
    word_res_arr = []
    try:
        word_res_arr = str(word_res).split(" ")
    except:
        pass
    retVAl = False
    cnt = 0
    if len(word_res_arr) > 0:
        for w in word_res_arr:
            if w in word_tag:
                cnt = cnt + 1
        if cnt > (len(word_res_arr) / 2):
            retVAl = True
    return retVAl


def getRelatedSentenceArr(sentence, sentenceArr):
    preds = [str(w).lower() for (w, t, idx) in sentence if t == "PRED" or t == "NON_INGREDIENT_SPAN_VERB"]
    ingres = [str(w).lower() for (w, t, idx) in sentence if t == "INGREDIENTS"]
    retSent = []
    for sent in sentenceArr:
        boolSame = False
        cnt = 0
        preds2 = [str(w).lower() for (w, t, idx) in sent if t == "PRED" or t == "NON_INGREDIENT_SPAN_VERB"]
        ingres2 = [str(w).lower() for (w, t, idx) in sent if t == "INGREDIENTS"]
        for pred in preds2:
            tmp = [w for w in preds if w == pred]
            if (len(tmp)) > 0:
                boolSame = True
        if boolSame:
            if len(ingres2) > 0:
                for ing in ingres2:
                    tmp = [w for w in ingres if w == ing]
                    if len(tmp) > 0:
                        cnt = cnt + 1
        if (cnt > 0 and boolSame) or (len(ingres2) == 0 and boolSame):
            retSent = sent
            cnt = 0
    return retSent


def compareTwoDirection(result, taggedRes):
    tmp = 0.0
    if len(taggedRes) == len(result):
        for i in xrange(len(taggedRes)):
            tmp = tmp + compareTwoSameSentence(sentenceResult=result[i], sentenceTaggedData=taggedRes[i])
    """ else:
        for i in xrange(len(taggedRes)):
            relatedSent = getRelatedSentenceArr(taggedRes[i], result)
            if len(relatedSent) > 0:
                tmp = tmp + compareTwoSameSentence(sentenceResult=relatedSent, sentenceTaggedData=taggedRes[i])
    """
    if tmp != 0:
        return tmp / len(result)
    else:
        return None


def calculateResult():
    total = 0.0
    cnt = 0
    cnt2 = 0
    total2 = 0.0
    filenames = os.listdir(RESULTS_URL)
    for i, file_name in enumerate(filenames):
        annotatedFilePath = os.path.join(ANNOTATED_URL, file_name)
        resultFilePath = os.path.join(RESULTS_URL, file_name)
        if os.path.isfile(resultFilePath) and os.path.isfile(annotatedFilePath):
            print i, "ii", file_name
            taggedData = UtilsIO.readPaperDataForGraph(annotatedFilePath)
            resultData = UtilsIO.readTheResultFromTheAlg(resultFilePath)
            if len(resultData) != len(taggedData):
                print len(resultData), "respath"
                print len(taggedData), "annotated path"
            value = compareTwoDirection(resultData, taggedData)
            precision = compareTwoDirection(taggedData, resultData)
            if value != None:
                total = total + value
                cnt = cnt + 1
            if precision != None:
                total2 = total2 + precision
                cnt2 = cnt2 + 1

    recall = (total / cnt) * 100
    precision = (total2 / cnt2) * 100
    f1 = 2 / ((1 / recall) + (1 / precision))

    print "counter 1 : ", cnt, "counter 2 : ", cnt2
    return [("f1", f1), ("precision", precision), ("recall", recall)]


def calculateResult(result_url, annotated_url, Ispaper):
    total = 0.0
    cnt = 0
    cnt2 = 0
    total2 = 0.0
    filenames = os.listdir(result_url)
    for i, file_name in enumerate(filenames):
        annotatedFilePath = os.path.join(annotated_url, file_name)
        resultFilePath = os.path.join(result_url, file_name)
        if os.path.isfile(resultFilePath) and os.path.isfile(annotatedFilePath):

            if Ispaper:
                taggedData = UtilsIO.readPaperDataForGraph_chunked(annotatedFilePath)
                resultData = UtilsIO.readPaperDataForGraph_chunked(resultFilePath)
            else:
                taggedData = UtilsIO.readPaperDataForGraph(annotatedFilePath)
                resultData = UtilsIO.readTheResultFromTheAlg(resultFilePath)

            value = compareTwoDirection(resultData, taggedData)
            precision = compareTwoDirection(taggedData, resultData)
            if value != None:
                total = total + value
                cnt = cnt + 1
            if precision != None:
                total2 = total2 + precision
                cnt2 = cnt2 + 1

    recall = (total / cnt) * 100
    precision = (total2 / cnt2) * 100
    f1 = 2 / ((1 / recall) + (1 / precision))

    print "counter : ", cnt, "counter 2 : ", cnt2
    return [("f1", f1), ("precision", precision), ("recall", recall)]


print calculateResult(RESULTS_URL2, ANNOTATED_URL2, True)
print("-------------------------")
print calculateResult(RESULTS_URL3, ANNOTATED_URL2, False)
print("-------------------------")
print calculateResult(RESULTS_URL, ANNOTATED_URL, False)

"""   counter :  29
       result :  0.764708013822
        """
